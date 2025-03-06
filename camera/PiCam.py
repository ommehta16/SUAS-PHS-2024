from picamera2 import Picamera2, Preview

import numpy as np
from time import sleep
import os

from PIL import Image #python imaging library

import io #file input stuff

def getFrame() -> np.ndarray:
    
    #home_dir = os.environ['HOME'] #set the location of your home directory

    cam = Picamera2()

    cam.start()
    # cam.start_preview() #starts camera preview
    sleep(0.1)
    return np.array(cam.capture_image('main'))

    #cam.take_photo(f"{home_dir}/Desktop/new_image"+str(i)+".jpg") #save the image to your desktop
        
    # memoryStream = io.BytesIO()
    # cam.capture(memoryStream, format = 'jpeg')
    # memoryStream.seek(0)

    # #convert image to np array
    # image = Image.open(memoryStream)
    # imageArray = np.array(image) #converts image to array

    #print("Captured Image: "+str(i))

    return imageArray
