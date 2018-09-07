#!/usr/bin/env python

"""
The purpose of this script is to subscribe to a video topic in ROS,
then convert it to OpenCV format, and then save it to a video file.
A script in need is a script indeed.
"""

import rospy
import roslib
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
import cv2
import datetime

class RosVideoSaver():
  def __init__(self):
    """
    Parameters and settings:
    Note that if params exist, these may get updated.
    Video filename will have time-stamp of YYYY-MM-DD_HH-MM-SS appended to it
    """
    self.image_width = 640
    self.image_height = 480
    self.image_topic = "pseudo_video_node"
    self.path = "/home/ubuntu/python_ws/davis_ai/"
    self.filename = "video"
    self.frame_rate = 10
    self.fourcc = cv2.cv.CV_FOURCC(*'XVID')
    self.cv_image = []
    self.c = 0
    self.verbose = True
    self.display = True
    
    """
    What does the params say?
    """
    #load up parameters
    if rospy.has_param('~image_width'):
      self.IMAGE_WIDTH = rospy.get_param('~image_width')
    if rospy.has_param('~image_height'):
      self.IMAGE_HEIGHT = rospy.get_param('~image_height')
    if rospy.has_param('~image_topic'):
      self.image_topic = rospy.get_param('~image_topic')
    if rospy.has_param('~save_path'):
      self.path = rospy.get_param('~save_path')
    if rospy.has_param('~save_filename'):
      self.filename = rospy.get_param('~save_filename')
    if rospy.has_param('~save_framerate'):
      self.frame_rate = rospy.get_param('~save_framerate')
    if rospy.has_param('~verbose'):
      self.verbose = rospy.get_param('~verbose')
    if rospy.has_param('~display'):
      self.filename = rospy.get_param('~display')
    
    # append date-time stamp to filename
    stamp = datetime.datetime.now()
    self.filename = self.filename +"_"+str(stamp.year)+"-"+str(stamp.month)+"-"+str(stamp.day)+"_"+str(stamp.hour)+"-"+str(stamp.minute)+"-"+str(stamp.second)
    
    self.video = cv2.VideoWriter(self.path+self.filename+".avi",
                                self.fourcc,
                                self.frame_rate,
                                (self.image_width,self.image_height))  # filename, ~, frame_rate, size)

    if self.verbose:
      print("********* PARAMS *********")
      print("Image width           :" + str(self.image_width))
      print("Image height          :" + str(self.image_height))
      print("Image topic           :" + str(self.image_topic))
      print("Save to               :" + str(self.path+self.filename+".avi"))
      print("Save frame rate       :" + str(self.frame_rate))
      print("**************************\n")

    #setup the cv bridge
    self.bridge = CvBridge()
    #subscribe to image
    self.image_sub = rospy.Subscriber(self.image_topic, Image, self.image_callback)
    #setup timer callback
    self.timer = rospy.Timer(rospy.Duration(1.0/8.0), self.timer_callback)
    self.have_image = False
    

  def image_callback(self, im_msg):
    #convert from ros to cv
    self.cv_image = self.bridge.imgmsg_to_cv2(im_msg, "bgr8")
    #resize image in case its not in the size we want
    self.cv_image = cv2.resize(self.cv_image, (self.image_width, self.image_height))
    self.have_image = True

    (height,width,_) = self.cv_image.shape
    assert (height==self.image_height), "param:image_height != received image height"
    assert (width==self.image_width), "param:image_width != received image width"
    
    if self.display:
      cv2.imshow("Viewer", self.cv_image)
    
    if self.verbose:
      print("Writing frame " + str(self.c))
      self.c = self.c + 1
      

  def timer_callback(self, event):
    if(self.have_image):
      self.video.write(self.cv_image)
    else:
      print("frame skipped")
      
    #reset and wait for new data
    self.have_image = False


  def main(self):
    if not self.display:
      print("Video viewer disabled. To enable, check params")
    if not self.verbose:
      print("Verbose disabled")
    
    rospy.spin()
    cv2.destroyAllWindows()
    self.video.release()
    print("Video saved to : " + str(self.path+self.filename+".avi"))


if __name__=="__main__":
  # Initialize ROS node
  rospy.init_node('ros_video_saver_node', anonymous=True)
  print("Initialized ROS node to save video from a ROS topic\n")
  rvs = RosVideoSaver()
  
  if rvs.display:
    cv2.startWindowThread() #to make sure we can close it later on
    cv2.namedWindow("Viewer", 1)
  
  # run main
  rvs.main()
  
