# Copyright 2024 David Seyser
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     https://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
from openai import OpenAI
import logging
import coloredlogs
import sys
from datetime import datetime
import random
import requests
import csv

from catkinCompile import *
import CodeGenLLM as cg
import fitnessUtil as fu
import benchmarkTestCases as bt

parser = argparse.ArgumentParser(description='Generate code using LLM')
parser.add_argument("-a", "--api", type=str, help='what api to use, openai or ollama or google')
parser.add_argument("-m", "--model", type=str, help='what model to use')
parser.add_argument("-p", "--path", type=str, help='path to the catkin_ws')
parser.add_argument("-v", "--verbose",action=argparse.BooleanOptionalAction, default=False, help='enable verbose output') #no use currently, should be used to get verbose and non verbose output in the command line
parser.add_argument("-pf", "--prompt", type=str, help='the file with the inital prompts')   
parser.add_argument("-g", "--generations", type=int, help='the number of generations to run the genetic algorithm')
parser.add_argument("-b", "--benchmark", type=str, help='what type of benchmark is tested')
args = parser.parse_args()

api = args.api
model = args.model
wsPath = args.path

logLevel = logging.DEBUG if args.verbose else logging.INFO
coloredlogs.install(
    level=logLevel,
    fmt='%(asctime)s - %(levelname)s - %(message)s',
    level_styles={
        'debug': {'color': 'cyan'},
        'info': {'color': 'white'},
        'warning': {'color': 'yellow'},
        'error': {'color': 'red'},
        'critical': {'color': 'magenta'}
    }
)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
openai_logger = logging.getLogger("openai")
openai_logger.setLevel(logging.INFO)

def getPrompts(filename):
    with open(filename, 'r') as file:
        prompts = file.readlines()
    return [prompt.strip() for prompt in prompts]

def writeAndCompile(code, path):
    with open(f"{path}/src/test/src/test_cpp.cpp", "w") as file: 
            try:
                file.write(code)
            except Exception as e:
                logging.error(f"An error occurred: {e}")    
                
    try:
        logging.debug("starting catkin compilation")
        compile = catkinCompile(wsPath, args.verbose)#path to the catkin_ws is different from the path to the file
        logging.debug(f"Compilation result: {"success" if compile == 0 else "failed"}")
        return not compile #!RETURNS 0 IF SUCCESSFUL, SO THIS WAY I CAN LATER CHECK IF IT SUCCEEDED
        
    except Exception as e:
        logging.error(f"An error occurred: {e}")
            
def getFitness(code, prompt, benchmark):
    
    match benchmark:
        case "subscriber":
            benchmarkScore = bt.subTest("test")
        case "publisher":
            benchmarkScore = bt.pubTest("test")
        case "tf":
            pass
        case _:
            benchmarkScore = 1
    
    ka = 1
    kb = 3
    kc = 0.3
    kd = 0.9
    ke = 2
    kf = 1
    
    halsteadVolume = fu.halsteadVolume(code)
    levenDist = fu.LevenshteinDistance(code, 100) # is currently used to determine how close the code is to the ideal code
    complexity = fu.Complexity(code) #cyclomatic complexity, halstead, LOC, Comments
    promptLenght, codeLength = fu.CodePromptLength(prompt, code)
    logging.debug(f"Complexity: {complexity}, Levenshtein distance: {levenDist}, BenchmarkScore = {benchmarkScore}, Prompt/Code - Length = {promptLenght, codeLength}, Halstead Volume: {1/halsteadVolume}")
    
    fitness = ka * complexity + kb * 1/codeLength + kc * 1/promptLenght + kd * levenDist + ke * benchmarkScore + kf * halsteadVolume
    
    logging.warning(f"Fitness: {fitness}")
    return fitness


def crossover(parent1, parent2):
    #might be useful to use 'worse' prompt as parent2 randomly to get more diversity
    
    if not parent1 or not parent2:
        logging.error("One or both parents are empty.")
        return parent1 if parent1 else parent2

    parent1Words = parent1.split()
    parent2Words = parent2.split()

    if not parent1Words or not parent2Words:
        logging.error("One or both parents have no words.")
        return parent1 if parent1Words else parent2

    crossover_point = random.randint(1, min(len(parent1Words), len(parent2Words)) - 1)
    childWords = parent1Words[:crossover_point] + parent2Words[crossover_point:]

    child = ' '.join(childWords)
    logging.debug(f"Crossover result: {child}")

    return child

def mutate(child):
    #mutation of the string child
    if not child:
        logging.error("Child is empty.")
        return child
    
    
    #might not be the best way
    substitute = {
        "Publisher": ["Subscriber", "ServiceServer", "ServiceClient", "ActionServer", "ActionClient"],
        "Subscriber": ["Publisher", "ServiceServer", "ServiceClient", "ActionServer", "ActionClient"],
        "generate": ["create", "build", "construct", "design", "develop", "fabricate"],
        "callback": ["handler", "function", "routine", "method"],
        "topic": ["service", "action", "parameter"],
        "function": ["method", "routine", "procedure"],
        "import": ["include", "use"],
        "from": ["import from"],
    }
    
    words = child.split()
    
    #could be usefull to have different ways to mutate the word (sub, delete, adding)
    for i in range(len(words)):
        if random.random() < 0.6 and words[i] in substitute:
            alternative_words = substitute[words[i]]
            words[i] = random.choice(alternative_words)
            
    child = ' '.join(words)
    logging.critical(f"Mutation result: {child}")
    return child


def genetic_algorithm(population, generations):
    evaluatedPrompts = {}  # Cache for evaluated prompts and their fitness scores
    results = []
    
    for generation in range(generations):
        logging.info(f"Generation: {generation}")
        fitnessScores = {}

        for prompt in population:
            if prompt in evaluatedPrompts:
                fitnessScores[prompt] = evaluatedPrompts[prompt]
            else:
                try:
                    match api:
                        case "google":
                            raise NotImplementedError("Not available")

                        case "openai":
                            logging.debug(f"Generating code using {args.api} with model {args.model}")
                            code = cg.codeFromOpenai(prompt, model)
                            logging.debug("Generating successful")

                        case _:
                            logging.debug(f"Generating code using {args.api} with model {args.model}")
                            code = cg.codeFromOllama(prompt, model)
                            logging.debug("Generating successful")

                except NotImplementedError as nie:
                    logging.error(f"{nie}")
                    exit(1)

                except Exception as e:
                    logging.critical(f"An error occurred: {e}") 
                    raise

                if writeAndCompile(code, wsPath):
                    fitness = getFitness(code, prompt, args.benchmark)
                else:
                    fitness = 0

                fitnessScores[prompt] = fitness
                evaluatedPrompts[prompt] = fitness

                evaluatedPrompts[prompt] = fitnessScores[prompt]  # Cache the evaluated prompt
                results.append({'generation': generation, 'prompt': prompt, 'code': code, 'fitness': fitness})
                
        sortedPopulation = sorted(fitnessScores, key=fitnessScores.get, reverse=True)
        bestPrompts = sortedPopulation[:2]
        
        newPopulation = population.copy()  # Initialize with the entire current population
        
        # Use the best prompt as parent1 to create the next generation & for 90% of the time use the second best prompts as parent2 otherwise use a random prompt
        if random.random() < 0.7:
            parent1, parent2 = bestPrompts[:2]
        else:
            parent1 = bestPrompts[0]
            parent2 = random.choice(sortedPopulation)
        
        logging.debug(f"Creating child from '{parent1}' and '{parent2}'")
        
        child = crossover(parent1, parent2)
        mutated_child = mutate(child)

        if mutated_child not in evaluatedPrompts:
            newPopulation.append(mutated_child)

        population = newPopulation
        logging.debug(population)
        logging.debug(newPopulation)
        
        with open(f'geneticAlgoritm_{args.benchmark}_{args.model}_cpp.csv_V0', 'w', newline='') as csvfile:
            fieldNames = ['generation', 'prompt', 'code', 'fitness']
            writer = csv.DictWriter(csvfile, fieldnames=fieldNames)
            writer.writeheader()
            for result in results:
                writer.writerow(result)

    return sortedPopulation[0]


if __name__ == "__main__":
    
    startTime = datetime.now()
    
    if args.verbose:
        sys.tracebacklimit = 1
    else:
        sys.tracebacklimit = 0
    
    logging.info("Starting code generation")
    
    try:
        prompts = getPrompts(args.prompt) #returns a list of prompts / is inital population
        
    except FileNotFoundError:
        logging.error(f"File: {args.prompt} not found")

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        
    try:
        bestPrompt = genetic_algorithm(prompts, args.generations)
        
    except NameError as name:
        logging.error(name)       
        
    endTime = datetime.now()
    elapsedTime = endTime-startTime
    
    logging.info(f"Best prompt: {bestPrompt}")
    
    logging.info(f"Operation took: {elapsedTime}")
    sys.exit(0)
 
