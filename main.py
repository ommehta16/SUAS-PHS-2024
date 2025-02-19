import time
import math
import multiprocessing as mp

from mission_planner.plane import Plane
from mission_planner import planner
from mapping import map_maker

from pymavlink import mavutil, mavwp

DEBUG:bool = True
CONNECTION_PORT:str = 'udpin:localhost:14540'

# mavlink simulator ^

# CONNECTIONPORT = '/dev/serial0'
# for final deployment ^

# CONNECTIONPORT = '/dev/ttyAMA0'
# or this maybe? idk ^

def main():

    connection = mavutil.mavlink_connection(CONNECTION_PORT,baud=57600) # we're connected over wire, so shouldn't lose anything
    if (not DEBUG):
        connection.wait_heartbeat()
        print(f"Heartbeat recieved from {connection.target_system} via {connection.target_component}")

    susser = Plane(connection)

    # DOCS:
    # - mavlink/message_definitions/v1.0/common.xml
    # - https://mavlink.io/en/mavgen_python/
    # - https://mavlink.io/en/messages/common.html

    last_beat:float = time.time()

    TIME_INCREMENT:float = 0.5
    START = time.time()
    MAX_PULL_WAIT = 5

    plan_conn, tmp = mp.Pipe(duplex=True)
    tmp1, tmp2 = mp.Pipe(duplex = True)

    brain = mp.Process(target=planner.plan,args=(tmp,tmp1))
    mapper = mp.Process(target = map_maker.develop_map, args=(tmp2))
    
    brain.start()
    joined = False

    if DEBUG: plan_conn.send("loolololloololololol")
    lastPull = time.time()
    while True:
        now:float = time.time()

        if (now - last_beat >= 1.0):
            connection.mav.heartbeat_send(mavutil.mavlink.MAV_TYPE_ONBOARD_CONTROLLER,
                                          mavutil.mavlink.MAV_AUTOPILOT_INVALID, 0, 0, 0)
            last_beat = now
        susser.update_pos()
        
        while plan_conn.poll() and (time.time()-now < TIME_INCREMENT or now-lastPull >= MAX_PULL_WAIT):
            lastPull = time.time()
            newData = plan_conn.recv()

            # HOW SEND DATA
            if type(newData) == str:
                ...
            elif type(newData) == int:
                ...
            else:
                ...

        
            # activate drop mechanism -- make function, expect to just need set 1 GPIO high

        # pipe susser to planner process
        # pipe command changes from planner process
        #   what commands?

        # send changes to susser

        time.sleep(max(TIME_INCREMENT - float(time.time()-now),0))

        if (time.time()-START > 10) and not joined:
            brain.join()
            joined = True

if __name__ == "__main__": main()