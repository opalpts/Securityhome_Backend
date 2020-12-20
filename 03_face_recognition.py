from pushbullet import Pushbullet
import RPi.GPIO as GPIO
from time import sleep
import cv2
import numpy as np
import os
import time
from picamera import PiCamera
import subprocess

camera = PiCamera()
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read('/home/pi/trainer/trainer.yml')
cascadePath = "/home/pi/opencv/data/haarcascades/haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cascadePath);
pb = Pushbullet("o.1n25KipPCg4AL6FXZHlRgd5x0WxfSzy5")
print(pb.devices)

font = cv2.FONT_HERSHEY_SIMPLEX

#iniciate id counter
id = 0
flag = 0

# names related to ids: example ==> Marcelo: id=1,  etc
names = ['None','title','title'] 

# Initialize and start realtime video capture
cam = cv2.VideoCapture(0)
cam.set(3, 640) # set video widht
cam.set(4, 480) # set video height

# Define min window size to be recognized as a face
minW = 0.1*cam.get(3)
minH = 0.1*cam.get(4)

while True:

    ret, img =cam.read()
    img = cv2.flip(img, 1) # -1 Flip vertically
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale( 
        gray,
        scaleFactor = 1.2,
        minNeighbors = 5,
        minSize = (int(minW), int(minH)),
       )

    for(x,y,w,h) in faces:

        cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)

        id, confidence = recognizer.predict(gray[y:y+h,x:x+w])
        #print(id,confidence)

        # Check if confidence is less them 100 ==> "0" is perfect match 
        if (confidence < 100):
            id = names[id]
            confidence = "  {0}%".format(round(100 - confidence))
        else:
            id = "unknown"
            confidence = "  {0}%".format(round(100 - confidence))
            flag = 1
#             dev = pb.get_device('Galaxy S6 Edge')
#             push = dev.push_note("Alert!!", "Someone is in your house")
#             sleep(10000)
            
        
        cv2.putText(img, str(id), (x+5,y-5), font, 1, (255,255,255), 2)
        cv2.putText(img, str(confidence), (x+5,y+h-5), font, 1, (255,255,0), 1)  
    
    cv2.imshow('camera',img)
    
    
    if (flag == 1):
        print ("motion")
        dev = pb.get_device('Galaxy S6 Edge')
        push = dev.push_note("Alert!!", "Someone is in your house")
        push = dev.push_link("Play Sound", "172.20.10.6:5000/alert")
        camera.start_preview()
        sleep(5)
        camera.capture('/home/pi/Desktop/image.jpg')
        camera.stop_preview()
        with open("/home/pi/Desktop/image.jpg", "rb") as pic:
            file_data = pb.upload_file(pic, "image.jpg")
        push = pb.push_file(**file_data)
        
#         subprocess.Popen("sudo fswebcam image.jpg",shell=True).communicate()
        time.sleep(1)
        flag = 0
          
        
    k = cv2.waitKey(10) & 0xff # Press 'ESC' for exiting video
    if k == 27:
        break

# Do a bit of cleanup
print("\n [INFO] Exiting Program and cleanup stuff")
cam.release()
cv2.destroyAllWindows()