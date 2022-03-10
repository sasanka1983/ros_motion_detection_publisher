#!/usr/bin/env python3

import cv2
import rospy
import sys
from cv_bridge import CvBridge
from sensor_msgs.msg import Image

class motion_detection_publish:

   def __init__(self, video_port):
       self.video_port=video_port

   def publish_motion_detection(self):
        rospy.init_node("motion_detection_node",anonymous=True)
        sleep_rate = rospy.Rate(.1)
        img_pub=rospy.Publisher("motion_detection_node_image",Image,queue_size=20)   
        bridge=CvBridge() 

        cap=cv2.VideoCapture(self.video_port)

        ret1,frame1= cap.read()
        gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        gray1 = cv2.GaussianBlur(gray1, (21, 21), 0)
        #cv2.imshow('window',frame1)
        image_count=1
        while(not rospy.is_shutdown()):
            try:
                ret2,frame2=cap.read()
                gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
                gray2 = cv2.GaussianBlur(gray2, (21, 21), 0)
                
                deltaframe=cv2.absdiff(gray1,gray2)
                
                #cv2.imshow('delta',deltaframe)
                threshold = cv2.threshold(deltaframe, 30, 255, cv2.THRESH_BINARY)[1]
                threshold = cv2.dilate(threshold,None)
                #cv2.imshow('threshold',threshold)
                va1,countour,va2 = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                for i in countour:
                    if cv2.contourArea(i) > 306000:
                        print(cv2.contourArea(i))  
                        continue
                      
                    (x, y, w, h) = cv2.boundingRect(i)
                    cv2.rectangle(frame2, (x, y), (x + w, y + h), (0, 0, 255), 3)
                    img = bridge.cv2_to_imgmsg(frame2,'bgr8')
                    img_pub.publish(img)
                    print("published image {imagecount}" .format(imagecount=image_count) )   
                    image_count=image_count+1
                
                cv2.imshow('window',frame2)
                
                if cv2.waitKey(20) == ord('q'):
                    break
            except(KeyboardInterrupt):
                cap.release()
                cv2.destroyAllWindows();    
        cap.release()
        cv2.destroyAllWindows()

if __name__=='__main__':
    print("Capturing motion detected images at port {port}" .format(port=sys.argv[1]))
    this_obj=motion_detection_publish(sys.argv[1])
    this_obj.publish_motion_detection()
