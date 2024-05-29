import subprocess
import os

def catkinCompile(path, verbose=False):
    try:
        #If result is 0, then the command was successful
        stdout = None if verbose else subprocess.DEVNULL
        stderr = None if verbose else subprocess.DEVNULL 

        result = subprocess.call("catkin_make", shell=True, cwd=path, stdout=stdout, stderr=stderr)
        return result
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    result = test_catkin("/mnt/d/test_ws")
    print(result)

