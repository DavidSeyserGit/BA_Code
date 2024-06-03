import requests
from openai import OpenAI
import re
import logging

def codeFromGoogle(prompt, api, model):
    return None
        
def codeFromOpenai(prompt, model):
    client = OpenAI()
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are an expert in ROS (Robot Operating System) programming with extensive experience in developing robust, efficient, and maintainable code. Your task is to generate clean, well-documented, and easy-to-understand code for any ROS Node. Ensure that the code follows best practices, including modularity, readability, and reusability. Provide clear comments and documentation to help users understand the functionality and structure of the code. Additionally, include any necessary setup instructions and dependencies required to run the code successfully."},
            {"role": "user", "content": f"{prompt}"},
        ]
    )
    codeBlock = re.search(r'```(?:python|cpp)\n(.+?)\n```', completion.choices[0].message.content, re.DOTALL)
    code = codeBlock.group(1).strip() if codeBlock else None
    return code
        
def codeFromOllama(prompt, model):
    try:
        url = 'http://localhost:11434/api/generate' #ollama api url
        data = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        r = requests.post(url, json=data)
        if r.status_code == 200: #connection is succesful
            response_data = r.json()
            response = response_data.get('response') #filtering the output of the LLM to only the repsonse
            start_index = response.find("```") #filtering for the codeblock
            if start_index == -1:
                return None
            end_index = response.find("```", start_index + 3)
            if end_index == -1:
                return None 
            codeBlock = response[start_index + 3 : end_index].strip()
            if codeBlock.startswith("python"):
                codeBlock = codeBlock[len("python"):].strip()
            return codeBlock
        
    except Exception as e:
            logging.critical("Connection refused")
    