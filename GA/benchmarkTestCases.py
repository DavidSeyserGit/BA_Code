'''
This file is for the tests of the benchmark functionality
'''
import subprocess
import time
import select
import logging

def pubTest(pkgName):
    # Starting publisher code
    subprocess.run("source /opt/ros/noetic/setup.bash", shell=True, check=True, executable='/bin/bash')
    subprocess.run("source /home/david/catkin_ws/devel/setup.bash", cwd="/home/david", shell=True, check=True, executable='/bin/bash')
    
    try:
        subprocess.run(f"rosrun {pkgName} test.py", cwd="/home/david/", shell=True, check=True, executable='/bin/bash', timeout=5)
    except subprocess.CalledProcessError as e:
        logging.warning(f"Error running rosrun: {e}")
        return 0.9  # Considered as failed to start publisher
    # Return value is a modifier for the fitness function
    return 1.1

def subTest():
    #start the ROS code
    #publish a message (subprocess)
    #run the file
    #check if the file makes an output 
    pass

if __name__ == "__main__":
    result = pubTest("test")
    print(result)