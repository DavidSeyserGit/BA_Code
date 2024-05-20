import subprocess
import os

def test_catkin():
    try:
        #If result is 0, then the command was successful
        result = subprocess.call("catkin_make",shell=True, cwd="/mnt/d/test_ws")
    except Exception as e:
        print(f"An error occurred: {e}")

test_catkin()