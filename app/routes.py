import sys
import flask
import cv2
import os
import pymysql as pymysql
from app import app
from flask import request, jsonify
import numpy as np
from PIL import Image
import time
import RPi.GPIO as GPIO
from pygame import mixer
conn = pymysql.connect(host = 'localhost', port=3306 , user= 'admin', passwd='123', db='securityhome')

@app.route('/')
@app.route('/index')
def index():
    return "Hello, World!"

@app.route('/camera', methods=["POST"])
def camera():
    cur = conn.cursor()
    try:
        name = request.json['name']
        sql = "INSERT INTO person (name_person) VALUES ('" + name + "') "
        cur.execute(sql)
        conn.commit()
        
        cur.execute("SELECT * FROM person WHERE name_person = '" + name + "' ")
        records = cur.fetchall()

        for row in records:
            print(row[0])
            data = row[0]
            print('id = '+str(data))
            id = row[0]
            print('id = '+str(data))
            
        cam = cv2.VideoCapture(0)
        cam.set(3, 640) # set video width
        cam.set(4, 480) # set video height

        face_detector = cv2.CascadeClassifier('/home/pi/Downloads/haarcascade_frontalface_default.xml')
        face_id = id
        #face_id = input('\n enter user id end press <return> ==>  ')

        print("\n [INFO] Initializing face capture. Look the camera and wait ...")
        count = 0

        while(True):
            ret, img = cam.read()
            img = cv2.flip(img, 1) # -1 flip video image vertically
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_detector.detectMultiScale(gray, 1.3, 5)
            for (x,y,w,h) in faces:
                cv2.rectangle(img, (x,y), (x+w,y+h), (255,0,0), 2)     
                count += 1
                cv2.imwrite("/home/pi/FacialRecognitionProject/dataset/User." + str(face_id) + "." + str(count) + ".jpg", gray[y:y+h,x:x+w])
                cv2.imshow('image', img)
            k = cv2.waitKey(100) & 0xff # Press 'ESC' for exiting video
            if k == 27:
                break
            elif count >= 30: # Take 30 face sample and stop video
                 break

# Do a bit of cleanup
        print("\n [INFO] Exiting Program and cleanup stuff")
        cam.release()
        cv2.destroyAllWindows()
        
        path = '/home/pi/FacialRecognitionProject/dataset'

        recognizer = cv2.face.LBPHFaceRecognizer_create()
        detector = cv2.CascadeClassifier("/home/pi/Downloads/haarcascade_frontalface_default.xml");

# function to get the images and label data
        def getImagesAndLabels(path):

            imagePaths = [os.path.join(path,f) for f in os.listdir(path)]     
            faceSamples=[]
            ids = []

            for imagePath in imagePaths:

                PIL_img = Image.open(imagePath).convert('L') # convert it to grayscale
                img_numpy = np.array(PIL_img,'uint8')

                id = int(os.path.split(imagePath)[-1].split(".")[1])
                faces = detector.detectMultiScale(img_numpy)

                for (x,y,w,h) in faces:
                    faceSamples.append(img_numpy[y:y+h,x:x+w])
                    ids.append(id)

            return faceSamples,ids

        print ("\n [INFO] Training faces. It will take a few seconds. Wait ...")
        faces,ids = getImagesAndLabels(path)
        recognizer.train(faces, np.array(ids))

# Save the model into trainer/trainer.yml
        recognizer.write('/home/pi/trainer/trainer.yml') # recognizer.save() worked on Mac, but not on Pi

# Print the numer of faces trained and end program
        print("\n [INFO] {0} faces trained. Exiting Program".format(len(np.unique(ids))))
        return "success"
    
    except Exception as e:
        print("Error :", repr(e))
        return "failure "+repr(e)
    
@app.route('/alert', methods=["GET"])
def alert():
    # Pins definitions
        btn_pin = 4

        # Set up pins
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(btn_pin, GPIO.IN)

        # Initialize pygame mixer
        mixer.init()

        # Remember the current and previous button states
        current_state = True
        prev_state = True

        # Load the sounds
        sound = mixer.Sound('/home/pi/Downloads/PanicAlarm.wav')

        # If button is pushed, light up LED
        try:
            while (prev_state == True):
                current_state = GPIO.input(btn_pin)
                try:
                    if (current_state == False) and (prev_state == True):
                        sound.play()
                    prev_state = current_state
                except Exception as e:
                    print("Error :", repr(e))
                    return "failure "+repr(e)
            # When you press ctrl+c, this will be called
        finally:
            GPIO.cleanup()
        return "success"

@app.route("/login", methods=["POST"])
def account():
    cur = conn.cursor()
    try:
        email = request.json['email']
        pwd = request.json['pwd']
        select_query ="SELECT * FROM register WHERE email_register = '" + email + "' and pwd_register = '" + pwd + "' "
        cur.execute(select_query)
        records = cur.fetchall()
        if len(records) == 1:
            select_query = "SELECT * FROM register WHERE email_register = '" + email + "' and pwd_register = '" + pwd + "' and status = '0' "
            cur.execute(select_query)
            conn.commit()
            row = cur.fetchall()
            if len(row) == 1:
                sql = "UPDATE register SET status = '1' WHERE email_register = '" + email + "' and pwd_register = '" + pwd + "'"
                cur.execute(sql)
                conn.commit()
                return "success"
            else:
                return "logined"

        else:
            return "failure"
    except Exception as e:
        print("Error :", repr(e))
        return "failure"
        
@app.route("/register", methods=['POST'])
def register():
    cur = conn.cursor()
    try:
        email = request.json['email_register']
        pwd = request.json['pwd_register']
        name = request.json['name_register']
        tel = request.json['tel_register']
        address = request.json['address_register']
        sql = "INSERT INTO register (email_register,pwd_register,name_register,tel_register,address_register,status)" \
              "VALUES ('"+email+"','"+pwd+"','"+name+"','"+tel+"','"+address+"','0')"
        cur.execute(sql)
        conn.commit()
        return "success"

    except Exception as e:
        print("Error :", repr(e))
        return "failure"

@app.route("/logout",methods=['POST'])
def logout():
    cur = conn.cursor()
    try:
        email = request.json['email']
        sql = "UPDATE register SET status = '0' WHERE email_register = '" + email + "' "
        cur.execute(sql)
        conn.commit()
        return  "success"

    except Exception as e:
        print("Error :", repr(e))
        return "failure"

@app.route("/checkid",methods=['post'])
def checkid():
    cur = conn.cursor()
    try:
        email = request.json['email']
        cur.execute("SELECT * FROM register WHERE email_register = '" + email + "' ")
        data = [{
            'id_register': row[0],
            'name_register': row[1],
            'email_register': row[2],
            'address_register': row[5],
            'tel_register': row[4],
        } for row in cur.fetchall()]
        return jsonify(data)
    except Exception as e:
        print("Error :", repr(e))
        return

        if __name__ == '__main__':
            app.run(host="172.20.10.6", debug=True)
