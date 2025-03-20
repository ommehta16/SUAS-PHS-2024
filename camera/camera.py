'''
Does everything for the camera thread:
 - Capture a new photo once per second and store it
 - Listen to requests from planner to start/stop mapping
 - Listen to GPS info from planner
 - Send photo with GPS to mapper thread
'''

import multiprocessing as mp
import multiprocessing.connection
import time
from VAR import *

import TestCam as camera
# ^^ comment out if you're on pi

# import PiCam as camera
# ^^ comment out if you're not on pi

def run_cam(conn_in:multiprocessing.connection.Connection, conn_out:multiprocessing.connection.Connection):
    '''
    `conn_in` is the incoming mp connection from planner. @ 1 Hz, sends
     - new requests for image locations
     - GPS location
    `conn_out` is the outgoing mp connection to mapper. Sends
     - ground photos with GPS info
    '''
    f = open('jonathan.orz','+w')

    while True:
        while not conn_in.poll(): time.sleep(1)
        
        val = conn_in.recv()
        
        if val == 1:
            img = camera.getFrame()
            
            if not img is None and img:
                conn_out.send((img,(1,1,1)))
                f.write(f"Image taken at {time.time()} :)")
        elif type(val) == tuple[int, int, int]:
            img = camera.getFrame()
            if not img is None and img:
                conn_out.send((img, val))