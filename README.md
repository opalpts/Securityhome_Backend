# Securityhome_Backend

project was to develop a home security system that used facial recognition and Internet of Things Technology for the care and security of homes by analyzing the face of a person via CCTV with facial recognition technology and alert a mobile application automatically when a face does not match the face of a registered member. The process to teach the machine to learn the facial characteristics of family members used a training dataset developed with Python's OpenCV library. The system was divided into 2 parts: 1) Backend Service System, developed with Python on a Raspberry Pi that was connected to a CCTV camera and a speaker for the sounding the alarm, it also was responsible for providing various service functions for the mobile application that sends notifications and includes a face analysis function. The database was managed with MySQL; and 2) Front-end System of the mobile application runs on the Android operating system. Users can perform registration, add family member’s information, and call various services from Raspberry Pi developed which was all developed with Android Studio.

how to run project
- mkdir Securityhome_Backend
- cd Securityhome_Backend
- python -m venv venv
- venv\Scripts\activate
- (venv)  pip install flask
- (venv)  mkdir app
- (venv)  set FLASK_APP=app.py
- (venv)  flask run
