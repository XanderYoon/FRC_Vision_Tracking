# -*- coding: utf-8 -*-

# import the necessary packages 
from collections import deque 
import numpy as np 
import argparse 
import cv2
import imutils
from networktables import NetworkTables

# Setting ip address and network table
ip = "10.51.9.2"
NetworkTables.initialize(server = ip)
visiontable = NetworkTables.getTable("Vision Table")
  
# construct the argument parse and parse the arguments 
ap = argparse.ArgumentParser() 
ap.add_argument("-v", "--video", 
    help="path to the (optional) video file") 
ap.add_argument("-b", "--buffer", type=int, default=64, 
    help="max buffer size") 
args = vars(ap.parse_args()) 
# define the lower and upper boundaries of the "green" 
# ball in the HSV color space, then initialize the 
# list of tracked points 
greenLower = (0,0,222) 
greenUpper = (193,42,255) 
pts = deque(maxlen=args["buffer"]) 
  
# if a video path was not supplied, grab the reference 
# to the webcam 
if not args.get("video", False): 
    camera = cv2.VideoCapture(0) 
  
# otherwise, grab a reference to the video file 
else: 
    camera = cv2.VideoCapture(args["video"]) 
# keep looping 
while True: 
    # grab the current frame 
    (grabbed, frame) = camera.read() 
  
    # if we are viewing a video and we did not grab a frame, 
    # then we have reached the end of the video 
    if args.get("video") and not grabbed: 
        break 
  
    # resize the frame, blur it, and convert it to the HSV 
    # color space 
    frame = imutils.resize(frame, width=600) 
    # blurred = cv2.GaussianBlur(frame, (11, 11), 0) 
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV) 
  
    # construct a mask for the color "green", then perform 
    # a series of dilations and erosions to remove any small 
    # blobs left in the mask 
    mask = cv2.inRange(hsv, greenLower, greenUpper) 
    mask = cv2.erode(mask, None, iterations=2) 
    mask = cv2.dilate(mask, None, iterations=2) 
 
 
    # find contours in the mask and initialize  the current 
    # (x, y) center of the ball 
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, 
        cv2.CHAIN_APPROX_SIMPLE)[-2] 
    center = None 
  
    # only proceed if at least one contour was found 
    if len(cnts) > 0: 
        # find the largest contour in the mask, then use 
        # it to compute the minimum enclosing circle and 
        # centroid 
        # c = max(cnts, key=cv2.contourArea)
        dict_cnts = {}
        for contour in cnts:
            dict_cnts[cv2.contourArea(contour)] = contour
        sorted_dict = sorted(dict_cnts.items(), key=lambda x:x[0])
        if len(dict_cnts) >= 2:
            c1 = sorted_dict[-1][1]
            c2 = sorted_dict[-2][1]
        else:
            print("Dont see two contours")
            continue
        
        c = c1
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        x1 = x
        y1 = y
        print("Con 1", cv2.minEnclosingCircle(c) )
        M = cv2.moments(c) 
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])) 
  
        # only proceed if the radius meets a minimum size 
        if radius > 10: 
            # draw the circle and centroid on the frame, 
            # then update the list of tracked points 
            cv2.circle(frame, (int(x), int(y)), int(radius), 
                (0, 255, 0), 2) 
            cv2.circle(frame, center, 5, (0, 255, 0), -1)
            rect = cv2.minAreaRect(c)
            box = cv2.cv.BoxPoints(rect)
            box = np.int0(box)
            cv2.drawContours(frame, [box], 0, (0,0,255),2)
            visiontable.putNumber("Point1X", box[0][0])
            visiontable.putNumber("Point1Y", box[0][1])
            visiontable.putNumber("Point2X", box[1][0])
            visiontable.putNumber("Point2Y", box[1][1])
            visiontable.putNumber("Point3X", box[2][0])
            visiontable.putNumber("Point3Y", box[2][1])
            visiontable.putNumber("Point4X", box[3][0])
            visiontable.putNumber("Point4Y", box[3][1])
  
            
        c = c2
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        x2 = x
        y2 = y  
        print("Con 2", cv2.minEnclosingCircle(c) )
        M = cv2.moments(c) 
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])) 
    
        midpointx = int(((x2 - x1)/2) + x1)
        midpointy = int(y1 - ((y1 - y2)/2))
        print("Midpoint", (midpointx,midpointy))       
        visiontable.putNumber("MidpointX", midpointx)
        visiontable.putNumber("MidpointY", midpointy)
        
        # only proceed if the radius meets a minimum size 
        if radius > 10: 
            # draw the circle and centroid on the frame, 
            # then update the list of tracked points 
            cv2.circle(frame, (int(x), int(y)), int(radius), 
                (0, 255, 0), 2) 
            cv2.circle(frame, center, 5, (0, 255, 0), -1)
            rect = cv2.minAreaRect(c)
            box = cv2.cv.BoxPoints(rect)
            box = np.int0(box)
            cv2.drawContours(frame, [box], 0, (0,0,255),2)

        
    
        #red = [255,0,0]
        cv2.circle(frame, (midpointx, midpointy), 2, 
                (255, 0, 0), 2)
 
    lower_green = np.array([255,15,255]) 
    upper_green = np.array([255,18,255]) 
    mask = cv2.inRange(hsv, lower_green, upper_green) 
    res = cv2.bitwise_and(frame,frame,mask=mask) 
 
    cv2.imshow('fff',res) 
    cv2.imshow("Frame", frame) 
  
    # show the frame to our screen 
 
    key = cv2.waitKey(1) & 0xFF 
  
    # if the 'q' key is pressed, stop the loop 
    #if key == ord("q"): cv2
        #break 
  
# cleanup the camera and close any open windows 
camera.release() 
cv2.destroyAllWindows() 
 
 
 
