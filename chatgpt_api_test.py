# Copyright 2024 david
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

from openai import OpenAI
import re
import argparse
import /utility/catkin_test.py as ct

parser = argparse.ArgumentParser(description='Generate code using OpenAI ChatGPT')
parser.add_argument("-prompt", "--prompt", type=str, help='Prompt to generate code from')
args = parser.parse_args()

#create a openai instance
client = OpenAI()

#generate code
completion = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "system", "content": "you are a master programmer in ROS. You can generate clean and easy to understand code for any Node."},
    {"role": "user", "content": f"{args.prompt}"},
  ]
)

#print only the code
code_snippet = re.search(r'```(?:python|cpp)\n(.+?)\n```', completion.choices[0].message.content, re.DOTALL)
if code_snippet:
    code = code_snippet.group(1).strip()
    print(code)
else:
    print(completion.choices[0].message.content)


term = input()
match term:
  case "openai":
    print("openai")