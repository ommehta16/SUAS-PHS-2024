import time
import math
import multiprocessing as mp

from plane import Plane
import planner


from pymavlink import mavutil, mavwp

DEBUG:bool = True
CONNECTION_PORT:str = 'udpin:localhost:14540'

# mavlink simulator ^

# CONNECTIONPORT = '/dev/serial0'
# for final deployment ^

# CONNECTIONPORT = '/dev/ttyAMA0'
# or this maybe? idk ^

def main():

    connection = mavutil.mavlink_connection(CONNECTION_PORT,baud=57600)
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

    conn, plan_conn = mp.Pipe(duplex=True)

    a = mp.Process(target=planner.plan,args=(plan_conn,))
    
    a.start()
    joined = False

    conn.send("loolololloololololol")
    lastPull = time.time()
    while True:
        now:float = time.time()

        if (now - last_beat >= 1.0):
            connection.mav.heartbeat_send(mavutil.mavlink.MAV_TYPE_ONBOARD_CONTROLLER,
                                          mavutil.mavlink.MAV_AUTOPILOT_INVALID, 0, 0, 0)
            last_beat = now
        susser.update_pos()
        
        while conn.poll() and (time.time()-now < TIME_INCREMENT or now-lastPull >= MAX_PULL_WAIT):
            lastPull = time.time()
            newData = conn.recv()

            # HOW SEND DATA
            if type(newData) == str:
                ...
            elif type(newData) == int:
                ...
            else:
                ...
        # pipe susser to planner process
        # pipe command changes from planner process
        #   what commands?

        # send changes to susser

        time.sleep(max(TIME_INCREMENT - float(time.time()-now),0))

        if (time.time()-START > 10) and not joined:
            a.join()
            joined = True

if __name__ == "__main__": main()