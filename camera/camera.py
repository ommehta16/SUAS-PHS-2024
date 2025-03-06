import multiprocessing as mp
import multiprocessing.connection
import time

import TestCam as camera
# ^^ comment out if you're on pi

# import PiCam as camera
# ^^ comment out if you're not on pi

def run_cam(conn_in:multiprocessing.connection.Connection, conn_out:multiprocessing.connection.Connection):
    f = open('jonathan.orz','+w')

    while True:
        while not conn_in.poll(): time.sleep(1)
        
        val = conn_in.recv()
        
        if val == 1:
            img = camera.getFrame()
            
            if not img is None and img:
                conn_out.send(img)
                f.write(f"Image taken at {time.time()} :)")
        
        else: crashout()
    

def crashout():
    ...