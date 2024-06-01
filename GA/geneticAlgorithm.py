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

from catkinCompile import *
import CodeGenLLM as cg
import fitnessUtil as fu

parser = argparse.ArgumentParser(description='Generate code using LLM')
parser.add_argument("-a", "--api", type=str, help='what api to use, openai or ollama or google')
parser.add_argument("-m", "--model", type=str, help='what model to use')
parser.add_argument("-p", "--path", type=str, help='path to the catkin_ws')
parser.add_argument("-v", "--verbose",action=argparse.BooleanOptionalAction, default=False, help='enable verbose output') #no use currently, should be used to get verbose and non verbose output in the command line
parser.add_argument("-pf", "--prompt", type=str, help='the file with the inital prompts')
parser.add_argument("-g", "--generations", type=int, help='the number of generations to run the genetic algorithm')
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
    with open(f"{path}/src/test/src/test.py", "w") as file: 
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
            
def getFitness(code, prompt):
    #fitness should be maximized for the code to be good
    codeLenth, promptLength = fu.CodePromptLength(code, prompt, 3, 1)
    levenDist = fu.LevenshteinDistance(code, 10)
    fitness = 1/codeLenth + levenDist
    return fitness


def crossover(parent1, parent2):
    if not parent1 or not parent2:
        logging.error("One or both parents are empty.")
        return parent1 if parent1 else parent2

    parent1Words = parent1.split()
    parent2Words = parent2.split()

    if not parent1Words or not parent2Words:
        logging.error("One or both parents have no words.")
        return parent1 if parent1Words else parent2

    crossover_point = min(len(parent1Words), len(parent2Words)) // 2
    childWords = parent1Words[:crossover_point] + parent2Words[crossover_point:]

    child = ' '.join(childWords)
    logging.debug(f"Crossover result: {child}")

    return child


def mutate(child):
    if not child:
        logging.error("Child is empty.")
        return child
    
    substitutionWords = {
        'nouns': ['node', 'topic', 'message', 'service', 'client', 'action', 'callback', 'event', 'handler', 'object', 'method', 'class', 'module', 'function', 'procedure', 'thread', 'process', 'signal', 'slot', 'interface', 'instance', 'attribute', 'property', 'element', 'entity'],
        'type': ['publish', 'subscribe', 'loop'],
        'actions': ['code', 'create', 'design', 'generate', 'make']
    }
    
    words = child.split()
    num_words = len(words)

    for i in range(len(words)):
        mutationType = random.random()
        
        if mutationType < 0.8: 
            # Substituting based on the context of the current word
            current_word = words[i]
            if current_word in substitutionWords['nouns']:
                words[i] = random.choice(substitutionWords['nouns'])
            elif current_word in substitutionWords['type']:
                words[i] = random.choice(substitutionWords['type'])
            elif current_word in substitutionWords['actions']:
                words[i] = random.choice(substitutionWords['actions'])
            
        elif mutationType < 0.04 and num_words > 1: 
            words.pop(i)
            num_words -= 1  
            
        elif mutationType < 0.2: 
            newWord = random.choice(substitutionWords['nouns'] + substitutionWords['type'])
            words.insert(i, newWord)
            num_words += 1
        
    mutatedPrompt = ' '.join(words)
    logging.warning(f"Mutation result: {mutatedPrompt}")
    return mutatedPrompt



def genetic_algorithm(population, generations):
    evaluatedPrompts = {}  # Cache for evaluated prompts and their fitness scores

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

                compile = writeAndCompile(code, wsPath)
                if compile:
                    fitnessScores[prompt] = getFitness(code, prompt)
                else:
                    fitnessScores[prompt] = 0  # Assign 0 fitness if compilation fails

                evaluatedPrompts[prompt] = fitnessScores[prompt]  # Cache the evaluated prompt

        sorted_population = sorted(fitnessScores, key=fitnessScores.get, reverse=True)
        best_prompts = sorted_population[:2]

        new_population = sorted_population.copy()

        parent1, parent2 = best_prompts[:2]
        
        logging.debug(f"Creating child from '{parent1}' and '{parent2}'")
        
        child = crossover(parent1, parent2)
        mutated_child = mutate(child)

        if mutated_child not in evaluatedPrompts:
            new_population.append(mutated_child)

        population = new_population
        logging.debug(population)
        logging.debug(sorted_population)

    return sorted_population[0]  # Return the best prompt from the final generation



#for testing purposes
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
         
    logging.info("End of Program")
                
