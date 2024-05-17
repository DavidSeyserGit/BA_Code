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

#TODO: add a case where either ollama or google api is used for different models

import requests
import random
import string
import argparse

parser = argparse.ArgumentParser(description='Generate code using LLM')
parser.add_argument("-api", "--api", type=str, help='what api to use, openai or ollama or google')
parser.add_argument("-model", "--model", type=str, help='what model to use')
args = parser.parse_args()

def getPrompts(filename):
    with open(filename, 'r') as file:
        prompts = file.readlines()
    return [prompt.strip() for prompt in prompts]


#needs to be modified to also include CHATGPT & Gemini1.5Flash
def getCodeFromLLM(prompt):
    match parser.model:
        case "google":
            return None
        case "openai":
            pass
        case _:
            url = 'http://localhost:11434/api/generate'
            data = {
                "model": "phi3", #TODO: needs to be a argument in the command line later
                "prompt": prompt,
                "stream": False
            }
            r = requests.post(url, json=data)
            if r.status_code == 200: #connection is succesful
                response_data = r.json()
                response = response_data.get('response')
                start_index = response.find("```")
                if start_index == -1:
                    return None
                end_index = response.find("```", start_index + 3)
                if end_index == -1:
                    return None 
                codeBlock = response[start_index + 3 : end_index].strip()
                if codeBlock.startswith("python"):
                    codeBlock = codeBlock[len("python"):].strip()
                return codeBlock

def getFitness(code):
    #write the code to a file and make a compilation test
    #make a levenshtein distance test
        # https://www.geeksforgeeks.org/introduction-to-levenshtein-distance/
    #code complexity test
    pass

def crossover(parent1, parent2):
    pass

def mutate(child):
    pass

def genetic_algorithm(population, generations):
    for _ in range(generations):
        fitness_scores = {}
        for prompt in population:
            code = getCodeFromLLM(prompt)
            if code:
                fitness_scores[prompt] = getFitness(code)
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

if __name__ == "__main__":
    
    #currently just writes the code to a file -> will be in fitness or seperate function later
    prompts = getPrompts("example1.txt")
    for prompt in prompts:
        code = getCodeFromLLM(prompt)
        if code:
            with open("test.py", "w") as file:
                file.write(code)
            print("CODE!")
