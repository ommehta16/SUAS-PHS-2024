import time
import math
import multiprocessing as mp

from mission_planner.plane import Plane
from mission_planner import planner
from mapping import map_maker

from pymavlink import mavutil, mavwp
from pymavlink.dialects.v20 import common as mavlink2

from VAR import *

def add_fence(master) -> None:
    wps:list[tuple[int]] = GEOFENCE
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
        
        send_wps(wps)

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
    master = mavutil.mavlink_connection(CONNECTION_PORT,baud=57600) # we're connected over wire, so shouldn't lose anything

    if (not DEBUG):
        master.wait_heartbeat()
        print(f"Heartbeat recieved from {master.target_system} via {master.target_component}")

    plane = Plane(master)

    last_beat:float = time.time()

    TIME_INCREMENT:float = 0.5
    START = time.time()
    MAX_PULL_WAIT = 5

    add_fence(master) # ADD GEOFENCE!

    plan_conn, tmp = mp.Pipe(duplex=True)
    tmp1, tmp2 = mp.Pipe(duplex = True)

    brain = mp.Process(target = planner.run_plan,args=(tmp,tmp1))
    mapper = mp.Process(target = map_maker.develop_map, args=(tmp2))
    
    brain.start()
    mapper.start()
    joined = False
    
    lastPull = time.time()
    
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