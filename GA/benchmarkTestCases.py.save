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
    subprocess.run("rosnode kill -a", shell=True, executable='/bin/bash')

def rosEnviroment():
    try:
        subprocess.run("source /opt/ros/noetic/setup.bash", shell=True, check=True, executable='/bin/bash')
        subprocess.run("source /home/david/catkin_ws/devel/setup.bash", cwd="/home/david", shell=True, check=True, executable='/bin/bash')
    except subprocess.CalledProcessError as e:
        logging.error(f"Error setting up environment: {e}")
     
def killProcess(proc):
    try:
        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
    except Exception as e:
        logging.error(f"Error killing process {proc.pid}: {str(e)}")
        

def pubTest(pkgName):
    logging.basicConfig(level=logging.INFO)
    rosEnviroment() #setting the enviroment variables for ROS
    rosCleanUp() #deleting the ROS nodes
    topicsBefore = list_topics()
    logging.info(f"Topics before running publisher: {topicsBefore}")

    logging.info("Running rosrun command")
    publisher = subprocess.Popen(f"rosrun {pkgName} test_cpp.cpp", cwd="/home/david/", shell=True, executable='/bin/bash', preexec_fn=os.setsid)

    time.sleep(3)

    topicsAfter = list_topics()
    logging.info(f"Topics after running publisher: {topicsAfter}")

    newTopics = topicsAfter - topicsBefore
    if not newTopics:
        logging.warning("No new topics detected")
        os.killpg(os.getpgid(publisher.pid), signal.SIGTERM)
        return 0.7

    new_topic = newTopics.pop()
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
            return 2
        else:
            logging.warning("No data received from publisher")
            return 0.7
        
    except subprocess.TimeoutExpired:
        logging.warning("No data received from publisher within timeout")
        return 0.7
    
    finally:
        os.killpg(os.getpgid(publisher.pid), signal.SIGTERM)

def subTest(pkgName):
    logging.basicConfig(level=logging.INFO)
    rosEnviroment()  # Setting the environment variables for ROS
    rosCleanUp()  # Deleting the ROS nodes
    
    topicsBefore = list_topics()
    logging.info(f"Topics before running subscriber: {topicsBefore}")
    
    subscriber = subprocess.Popen(
        f"rosrun {pkgName} test.py",
        cwd="/home/david/",
        shell=True,
        executable='/bin/bash',
        preexec_fn=os.setsid,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    time.sleep(3)  # Wait for the subscriber to initialize

    topicsAfter = list_topics()
    newTopics = set(topicsAfter) - set(topicsBefore)
    logging.info(f"Topics after running subscriber: {newTopics}")

    if not newTopics:
        logging.warning("No new topics detected")
        killProcess(subscriber)
        return 0.7

    newTopic = newTopics.pop()
    logging.info(f"Publishing to new topic: {newTopic}")
    publisher = subprocess.Popen(
        ["rostopic", "pub", "-r", "1", newTopic, "std_msgs/String", "hello"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid
    )
    
    rosout = subprocess.Popen(
        ["rostopic", "echo", "/rosout"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        preexec_fn=os.setsid
    )

    try:
        start_time = time.time()
        while time.time() - start_time < 10:
            if rosout.poll() is not None:
                logging.info("rosout process ended unexpectedly")
                break

            line = rosout.stdout.readline()
            if line:
                logging.info("Subscriber received a message")
                return 2
                    
    except Exception as e:
        logging.error(f"Exception occurred: {str(e)}")
        return False
    finally:
        killProcess(rosout)
        killProcess(publisher)
        killProcess(subscriber)

    logging.warning("Timeout: Subscriber did not receive a message in time")
    return 0.7
            
def tfTest(pkgName):
    return 1
 
def motorcontrollerTest(pkgName):
    return 1
      
if __name__ == "__main__":
    result = subTest("test")
    print(result)
    
