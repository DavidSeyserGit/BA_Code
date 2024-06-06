'''
This file is for the tests of the benchmark functionality
'''
import subprocess
import time
import select


def pubTest():
    # code to start the ROS code
    
    # subprocess for checking if code publishes
    process = subprocess.Popen("rostopic echo /chatter", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    dataReceived = False
    timeout = 10  # seconds
    startTime = time.time()

    while True:
        if time.time() - startTime > timeout:
            break

        # Use select to wait for data or timeout
        readable, _, _ = select.select([process.stdout], [], [], timeout - (time.time() - startTime))
        
        if readable:
            line = process.stdout.readline()
            if line:
                dataReceived = True
                break

    process.terminate()  # Terminate the process
    #return value is a modifer for the fitness function
    return (1.1 if dataReceived else 0.9)


def subTest():
    #start the ROS code
    #publish a message (subprocess)
    #run the file
    #check if the file makes an output 
    pass

if __name__ == "__main__":
    result = pubTest()
    print(result)