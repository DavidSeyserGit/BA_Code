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

    codeLenth, promptLength = fu.CodePromptLength(code, prompt, 1, 1)

    return promptLength / codeLenth

def crossover(parent1, parent2):
    parent1Words = parent1.split()
    parent2Words = parent2.split()
    
    # Determine the crossover point within the range of the shorter parent's length
    crossover_point = min(len(parent1Words), len(parent2Words)) // 2

    # Ensure the crossover point is within a sensible range
    if len(parent1Words) == 0 or len(parent2Words) == 0:
        return parent1 if len(parent1Words) > 0 else parent2

    # Create the child by combining parts of parent1 and parent2
    childWords = parent1Words[:crossover_point] + parent2Words[crossover_point:]

    # Join the words back into a string
    child = ' '.join(childWords)
    
    return child

def mutate(child):
    #mutate the child randomly by swapping/adding/subtracting words from the prompt.
    substitutionWords = ['node', 'topic', 'message', 'publish', 'subscribe', 'service', 'client', 'action', 'goal', 'result']
    
    # Split the prompt into words
    words = child.split()
    
    # Mutate the string
    for i in range(len(words)):
        if random.random() < 0.1:
            # Substitute the word at position i
            newWord = random.choice(substitutionWords)
            words[i] = newWord
    
    # Join the words back into a string
    mutatedPrompt = ' '.join(words)
    return mutatedPrompt


def genetic_algorithm(population, generations): #population are all prompts, might need to be changed later to use the getPrompt function
    for _ in range(generations):
        logging.info(f"Generation: {_}")
        fitness_scores = {}
        
        for prompt in population:
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
                fitness_scores[prompt] = getFitness(code, prompt)
            else:
                fitness_scores[prompt] = 0  # Assign 0 fitness if compilation fails

        sortedPopulation = sorted(fitness_scores, key=fitness_scores.get, reverse=True)
        bestPrompts = sortedPopulation[:2]
        
        #bestPrompts = sortedPopulation[:len(population) // 2]

        #! I need to make sure that i always have a minimum of 4 elements in the population
        newPopulation = population.copy()

        parent1, parent2 = bestPrompts[:2]
        
        logging.debug(f"Creating child from '{parent1}' and '{parent2}'")
            
        child = crossover(parent1, parent2)
        mutatedChild = mutate(child)
        
        newPopulation.append(mutatedChild)
        #new_population.append(mutated_child)
        
        population = newPopulation
        logging.debug(population)
        logging.debug(sortedPopulation)
        
    return sortedPopulation[0] #return the best prompt from the final




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
        bestPrompt = genetic_algorithm(prompts, 2)
        
    except NameError as name:
        logging.error(name)       
        
    endTime = datetime.now()
    elapsedTime = endTime-startTime
    
    logging.info(f"Best prompt: {bestPrompt}")
    
    logging.info(f"Operation took: {elapsedTime}")
         
    logging.info("End of Program")
                
