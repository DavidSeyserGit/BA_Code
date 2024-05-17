import rospy
from std_msgs.msg import String

def chatter_callback(data):
    print("Received: %s" % data.data)

def listener():
    rospy.init_node('chatter_listener', anonymous=True)
    rospy.Subscriber('/chatter', String, chatter_callback)
    r = rospy.Rate(10/float(rospy.get_param("~loop_rate")))
    while not rospy.is_shutdown():
        r.sleep()

if __name__ == '__main__':
    listener()