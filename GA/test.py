#!/usr/bin/env python

import rospy
from std_msgs.msg import String

def chatter_callback(msg):
    rospy.loginfo("I heard: %s", msg.data)

def chatter_subscriber():
    rospy.init_node('chatter_subscriber', anonymous=True)
    rospy.Subscriber('/chatter', String, chatter_callback)
    rospy.spin()

if __name__ == '__main__':
    chatter_subscriber()