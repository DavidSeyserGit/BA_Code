'''
This file is for the tests of the benchmark functionality
'''
import subprocess
import time
import select
import logging
import rostopic
import os
import signal

def list_topics():
    result = subprocess.run(["rostopic", "list"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return set(result.stdout.decode('utf-8').split())

def rosCleanUp():
    subprocess.run("rosnode cleanup", shell=True, check=True)

def rosEnviroment():
    try:
        subprocess.run("source /opt/ros/noetic/setup.bash", shell=True, check=True, executable='/bin/bash')
        subprocess.run("source /home/david/catkin_ws/devel/setup.bash", cwd="/home/david", shell=True, check=True, executable='/bin/bash')
    except subprocess.CalledProcessError as e:
        logging.error(f"Error setting up environment: {e}")

def pubTest(pkgName):
    logging.basicConfig(level=logging.INFO)
    rosEnviroment() #setting the enviroment variables for ROS
    rosCleanUp() #deleting the ROS nodes
    topics_before = list_topics()
    logging.info(f"Topics before running publisher: {topics_before}")

    logging.info("Running rosrun command")
    publisher_process = subprocess.Popen(f"rosrun {pkgName} test.py", cwd="/home/david/", shell=True, executable='/bin/bash', preexec_fn=os.setsid)

    time.sleep(3)

    topics_after = list_topics()
    logging.info(f"Topics after running publisher: {topics_after}")

    new_topics = topics_after - topics_before
    if not new_topics:
        logging.warning("No new topics detected")
        os.killpg(os.getpgid(publisher_process.pid), signal.SIGTERM)
        return 0.7

    new_topic = new_topics.pop()
    logging.info(f"Detected new topic: {new_topic}")

    try:
        echo_output = subprocess.run(
            ["rostopic", "echo", "-n1", new_topic],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5
        )
        if echo_output.stdout:
            logging.info(f"Received message: {echo_output.stdout.decode('utf-8')}")
            return 1.1
        else:
            logging.warning("No data received from publisher")
            return 0.7
    except subprocess.TimeoutExpired:
        logging.warning("No data received from publisher within timeout")
        return 0.7
    finally:
        os.killpg(os.getpgid(publisher_process.pid), signal.SIGTERM)
def subTest():
    #start the ROS code
    #publish a message (subprocess)
    #run the file
    #check if the file makes an output 
    pass

if __name__ == "__main__":
    result = pubTest("test")
    print(result)