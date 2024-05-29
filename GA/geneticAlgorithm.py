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

from catkinCompile import *
import CodeGenLLM as cg

parser = argparse.ArgumentParser(description='Generate code using LLM')
parser.add_argument("-a", "--api", type=str, help='what api to use, openai or ollama or google')
parser.add_argument("-m", "--model", type=str, help='what model to use')
parser.add_argument("-p", "--path", type=str, help='path to the catkin_ws')
parser.add_argument("-v", "--verbose",action=argparse.BooleanOptionalAction, default=False, help='enable verbose output') #no use currently, should be used to get verbose and non verbose output in the command line
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
                
            except Exception as e:
                logging.error(f"An error occurred: {e}")
            
def getFitness(code, prompt):
    promptLength = len(prompt)
    codeLenth = len(code)
    #maintainability index
    #make a levenshtein distance test
        # https://www.geeksforgeeks.org/introduction-to-levenshtein-distance/
        
    #every metric should have different weights and the max of the fitness function should be the best possible code
    pass

def crossover(parent1, parent2):
    pass

def mutate(child):
    #mutate the child randomly by swapping/adding/subtracting words from the prompt.
    #TODO: needs a way to change only certain parts of the prompt without loosing the meaning of the sentence
    pass

def genetic_algorithm(population, generations): #population are all prompts, might need to be changed later to use the getPrompt function
    for _ in range(generations):
        fitness_scores = {}
        for prompt in population:
            try:
                match api:
                    case "google":
                        raise NotImplementedError("Google not implemented yet")
            
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
            
            #exception handling when no code can be created
            except Exception as e:
                logging.critical(f"An error occurred: {e}")
                raise
            
            writeAndCompile(code, wsPath)
            #generate code -> compile code -> get fitness score
            #TODO: make sure code actually gets to the compile stage before getting the fitness score
            if code: #TODO: if compilation is successful
                fitness_scores[prompt] = getFitness(code, prompt)
            else:
                #throw a warning force fitness to be 0 for this prompt, and jumpt to the next prompt
                pass
                
        sortedPopulation = sorted(fitness_scores, key=fitness_scores.get, reverse=True)
        bestPrompts = sortedPopulation[:len(population) // 2]
        
        # Generate new population
        new_population = []
        for _ in range(len(population) - len(bestPrompts)):
            #first two elements of best prompt -> parent1, parent2
            parent1, parent2 = bestPrompts[:2]
            child = crossover(parent1, parent2)
            mutated_child = mutate(child)
            new_population.append(mutated_child)
        
        population = bestPrompts + new_population
    
    return max(fitness_scores, key=fitness_scores.get)





#for testing purposes
if __name__ == "__main__":
    
    logging.info("Starting code generation")
    prompts = getPrompts("example1.txt") #returns a list of prompts / is inital population
    genetic_algorithm(prompts, 10)
                
    logging.info("End of Program")
                
