# -*- coding: utf-8 -*-
"""
Created on Tue Apr 30 11:55:05 2019

@author: AI & ML
"""
import numpy as np
import socketio#for integrating with gain using server.
import eventlet
from flask import Flask
from keras.models import load_model#it is used for loading the model in the enviroment
import base64
from io import BytesIO#these are used for working with images.
from PIL import Image
import cv2

sio = socketio.Server()#used for creating the server.

app = Flask(__name__) #'__main__'#used for handling pourpose.

speed_limit = 30#for speed limit of the car.

def img_preprocess(img):
  img = img[60:135,:,:]
  img = cv2.cvtColor(img,cv2.COLOR_RGB2YUV)
  img = cv2.GaussianBlur(img, (3,3),0)
  img = cv2.resize(img,(200,66))
  img = img/255
  
  return img



@sio.on('telemetry')#send signal to your gain.

def telemetry(sid, data):
    speed = float(data['speed'])
    image = Image.open(BytesIO(base64.b64decode(data['image'])))#take image from gain.
    image = np.asarray(image)
    image = img_preprocess(image)
    image = np.array([image])
    steering_angle = float(model.predict(image))#predicting the steering angle.
    throttle = 1.0 - speed/speed_limit#predicting the throttle.
    print('{} {} {}'.format(steering_angle, throttle,speed))
    send_control(steering_angle,throttle)#sending the command.

@sio.on('connect')#message, disconnect#used for connecting the gain

def connect(sid, environ):
    print('connected')
    send_control(0,0)
    
def send_control(steering_angle,throttle):#using telementry send the image
    sio.emit('steer',data={
            'steering_angle':steering_angle.__str__(),
            'throttle':throttle.__str__()
            })
    

if __name__=='__main__':#loading the model which we have downloaded from google colab.
    model = load_model(r"D:\Courses\AI & ML\beta_simulator_windows\training data\model.h5")
    app = socketio.Middleware(sio,app)#for creating the tunnel in between.
    eventlet.wsgi.server(eventlet.listen(('',4567)),app)#used for code forwarding.
