import subprocess
import os

def catkinCompile(path):
    try:
        #If result is 0, then the command was successful
        result = subprocess.call("catkin_make",shell=True, cwd=path)
        return result
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    result = test_catkin("/mnt/d/test_ws")
    print(result)

