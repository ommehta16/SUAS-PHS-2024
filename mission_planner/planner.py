import multiprocessing as mp
import multiprocessing.connection
import time
from plane import Plane
from VAR import *

TIME_INCREMENT:float=0.5
MAX_PULL_WAIT=5

class Route:
    def __init__(self,wps:list[tuple[int]]):
        self.wps=wps


# We MIGHT need this...
def inFence(point:tuple[int,int]) -> bool:
    '''
    **NOT IMPLEMENTED YET 3/12/25**

    Test if the point with coordinates `point` is within the geofence area
    '''
    raise NotImplementedError()

    GEOFENCE # this is the geofence!

def run_plan(comm_conn:multiprocessing.connection.Connection, map_conn:multiprocessing.connection.Connection):
    '''
    This is the "main" function for the plan thread

    Takes in a connection to the main thread (`comm_conn`) and to the `mapper` thread
    '''
    while not comm_conn.poll():
        time.sleep(1)
    f = open('jonathan.orz','+w')

    val = comm_conn.recv()
    lastPull = time.time()
    plane = Plane()
    while True:
        now=time.time()


        while comm_conn.poll() and (time.time()-now < TIME_INCREMENT or now-lastPull >= MAX_PULL_WAIT):
            lastPull = time.time()
            newData = comm_conn.recv()

            # HOW SEND DATA
            if type(newData) is int:
                ...
            
            elif type(newData) is Plane:
                plane=newData
            
