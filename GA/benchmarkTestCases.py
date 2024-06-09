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
            return 2
        else:
            logging.warning("No data received from publisher")
            return 0.7
    except subprocess.TimeoutExpired:
        logging.warning("No data received from publisher within timeout")
        return 0.7
    finally:
        os.killpg(os.getpgid(publisher_process.pid), signal.SIGTERM)
        
        
def subTest(pkgName):
    logging.basicConfig(level=logging.INFO)
    rosEnviroment()  # Setting the environment variables for ROS
    rosCleanUp()  # Deleting the ROS nodes
    
    topics_before = list_topics()
    logging.info(f"Topics before running subscriber: {topics_before}")
    
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

    topics_after = list_topics()
    new_topics = topics_after - topics_before
    logging.info(f"Topics after running subscriber: {topics_after}")

    if not new_topics:
        logging.warning("No new topics detected")
        os.killpg(os.getpgid(subscriber.pid), signal.SIGTERM)
        return 0.7

    publishers = []
    for topic in new_topics:
        logging.info(f"Publishing to new topic: {topic}")
        publisher = subprocess.Popen(
            ["rostopic", "pub", "-1", topic, "std_msgs/String", "hello"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid
        )
        publishers.append(publisher)
    
    time.sleep(3)  # Give some time for the subscriber to receive the messages

    logging.info("Checking if the subscriber received the message")
    try:
        output, errors = subscriber.communicate(timeout=10)

        # Check if any message was received
        if output.strip() or errors.strip():  # Check if there is any non-empty output
            logging.info(f"Subscriber received a message: {output.strip()}\nErrors: {errors.strip()}")
            return 2
        else:
            logging.warning("Subscriber did not receive any message")
            return 0.7
        
    except subprocess.TimeoutExpired:
        logging.warning("Subscriber process timed out")
        return 0.7
    
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return 0.7
    
    finally:
        # Cleanup processes
        try:
            os.killpg(os.getpgid(subscriber.pid), signal.SIGTERM)
        except Exception as e:
            logging.error(f"Error killing subscriber process: {str(e)}")
        
        for publisher in publishers:
            try:
                os.killpg(os.getpgid(publisher.pid), signal.SIGTERM)
            except Exception as e:
                logging.error(f"Error killing publisher process: {str(e)}")


        
if __name__ == "__main__":
    result = subTest("test")
    print(result)