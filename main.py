import time
import math
import multiprocessing as mp

import sys, os

from mission_planner.plane import Plane
from mission_planner import planner
from mapping import map_maker
from camera import camera

from pymavlink import mavutil, mavwp
from pymavlink.dialects.v20 import common as mavlink2

from VAR import *

flight_num=0
while os.path.exists(f"logs/flight{flight_num}.log"): flight_num+=1
sys.stdout = open(f"logs/flight{flight_num}.log", 'w')


# dumb variables to make code more readable
MINUTE = 60
HOUR = 3600

def add_fence(master) -> None:
    wps:list[tuple[float,float,float]] = GEOFENCE
    for i, wp in enumerate(wps):
        master.mav.mission_item_send(
            target_system = master.target_system,
            target_component = master.target_component,
            seq=i, # waypoint number
            frame=mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
            command=mavutil.mavlink.MAV_CMD_NAV_FENCE_POLYGON_VERTEX_INCLUSION,
            current=0,  # We don't set it to the current waypoint
            autocontinue=1,  # Continue to the next waypoint
            param1=len(wps),  # 
            param2=int('NaN'),  #
            param3=int('NaN'),  #
            param4=int('NaN'),  #
            x=wp[0], # lat
            y=wp[1], # lon
            z=int('NaN'), # alt
        )

    master.mav.command_long_send(
        target_system = master.target_system,
        target_component = master.target_component,
        command=mavutil.mavlink.MAV_CMD_DO_FENCE_ENABLE,
        confirmation=0,
        param1=1, # 0 --> disable, 1 --> enable, 2 --> cooked
        param2=0, # 0 --> apply to all, otherwise=bitmasks for ones to do
        param3=float('NaN'),
        param4=float('NaN'),
        param5=float('NaN'),
        param6=float('NaN'),
        param7=float('NaN')
    )

    

def set_wps(wps: list[tuple], master) -> None:
        '''
        Set all waypoints to `wps`

        `wp[i]` in form lat, long, alt

        **Replaces** waypoint list
        '''
        master.mav.clear_all_send(
            target_system=master.target_system,
            target_component=master.target_component
        ) # clears all waypoints
        
        send_wps(wps,master)

def send_wps(wps: list[tuple], master) -> None:
        '''
        Send a list of waypoints (`wps`) in form (`lat`, `lon`,`alt`) to master

        Get **appended to** waypoint list
        '''
        master.mav.mission_count_send(
            target_system=master.target_system,
            target_component=master.target_component,
            count=len(wps),
        )

        for i, wp in enumerate(wps):
            master.mav.mission_item_send(
                target_system = master.target_system,
                target_component = master.target_component,
                seq=i, # waypoint number
                frame=mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                command=mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, # go to the waypoint, nothing fancy
                current=0,  # We don't set it to the current waypoint
                autocontinue=1,  # Continue to the next waypoint
                param1=0,  # Hold time (seconds)
                param2=0,  # Acceptance radius (meters)
                param3=0,  # Pass through radius (meters)
                param4=float('nan'),  # Yaw angle -- we don't care here
                x=wp[0], # lat
                y=wp[1], # lon
                z=wp[2], # alt
            )
            i+=1

        mode_id = master.mode_mapping()['AUTO']
        master.mav.set_mode_send(
            master.target_system,
            mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
            mode_id
        )

def main():
    try:
        master = mavutil.mavlink_connection(CONNECTION_PORT,baud=57600) # we're connected over wire, so shouldn't lose anything
        print(f"Connected on {CONNECTION_PORT}")
    except Exception as e:
        print(f"Could not connect to autopilot: {e}")
        exit()
    
    master.wait_heartbeat()
    print(f"Heartbeat recieved from {master.target_system} via {master.target_component}")

    # Arm = pixhawk does safety checks + turns on motors etc.
    master.mav.command_long_send(
        master.target_system,
        master.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
        0,
        1,          # 1 = arm, 0 = disarm
        0,0,0,0,0,0
    )
    print("arming system")
    start = time.time()
    armed = False

    while not armed:
        if time.time() > start + 1*MINUTE:
            raise TimeoutError("Timed out while arming")
            sys.exit(0)
        try:
            msg = master.recv_match(type="HEARTBEAT", blocking=True, timeout=1)
            if msg:
                if msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED:
                    armed=True
                    print("armed!")
        except Exception as e:
            print(f"Error recieving heartbeat: {e}")
            break
    if not armed:
        print(f"Could not arm the system. Check for pre-arm conditions.")
        sys.exit(1)

    plane = Plane(master)

    last_beat:float = time.time()

    TIME_INCREMENT:float = 0.5
    START = time.time()
    MAX_PULL_WAIT = 5

    add_fence(master) # ADD GEOFENCE!

    plan_conn, tmp = mp.Pipe(duplex=True)
    tmp1, tmp2 = mp.Pipe(duplex = True)

    brain = mp.Process(target = planner.run_plan,args=(tmp,tmp1))
    mapper = mp.Process(target = map_maker.develop_map, args=(tmp2,))
    cam = mp.Process(target = camera.run_cam, args=())
    
    brain.start()
    mapper.start()
    joined = False
    
    lastPull = time.time()

    # try to take off
    plane.takeoff()
    

    # For proof of flight, now has to:
    #  - generate + set waypoints
    #  - switch mode from LOITER to AUTO
    #  - track waypoint completion
    #  - land

    # 1 and 2 are easy
    # 3 and 4 depend on pymavlink api (need to research more)

    while True:
        now:float = time.time()

        if (now - last_beat >= 1.0):
            master.mav.heartbeat_send(mavutil.mavlink.MAV_TYPE_ONBOARD_CONTROLLER,
                                          mavutil.mavlink.MAV_AUTOPILOT_INVALID, 0, 0, 0)
            last_beat = now
        if plane.update_pos(): plan_conn.send(plane)

        while plan_conn.poll() and (time.time()-now < TIME_INCREMENT or now-lastPull >= MAX_PULL_WAIT):
            lastPull = time.time()
            newData = plan_conn.recv()

            # HOW SEND DATA
            if type(newData) == int: ...
            elif type(newData) == list[tuple]: 
                '''
                Set our current waypoints to newData
                
                newData[i] (in form lat, long, alt)
                '''

                set_wps(newData,master)


        time.sleep(max(TIME_INCREMENT - float(time.time()-now),0))

        if (time.time()-START > 10) and not joined:
            brain.join()
            joined = True

if __name__ == "__main__": main()