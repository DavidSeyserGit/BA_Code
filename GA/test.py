import rospy
from std_msgs.msg import String

def chatter_callback(msg):
    print(msg.data)

rospy.init_node('listener')
sub = rospy.Subscriber('/chatter', String, callback=chatter_callback)
rospy.spin()