from pymavlink import mavutil, mavwp
import time
import math

# https://ardupilot.org/dev/docs/raspberry-pi-via-mavlink.html
# 
# 
# Allan hardware stuff (?) ^
# you should be able to just connect to TELEM1 though and turn on pixhawk


# Branden can you pls do pi setup
# SETUP ON PI (https://forums.raspberrypi.com/viewtopic.php?t=347485 )
# 
# 1. Change Settings
#  sudo raspi-config
#    System > Boot/Auto-Login --> set console to auto login
# 2. Run script
#  nano ~/.bashrc
#     At bottom, add
#       path/to/.venv/python3 path/to/here/testflight.py
#

CONNECTIONPORT = '/dev/serial0'

connection = mavutil.mavlink_connection(CONNECTIONPORT,baud=57600)

connection.wait_heartbeat()

all_message = open("LOG.txt","a+")

start = time.time()

TWO_HOURS = 2 * 60 * 60

wanted = [
    mavutil.mavlink.GPS_RAW_INT,
    mavutil.mavlink.RAW_PRESSURE,
    mavutil.mavlink.ATTITUDE,
    mavutil.mavlink.SCALED_PRESSURE,
    mavutil.mavlink.GLOBAL_POSITION_INT,
    mavutil.mavlink.SYS_STATUS,
]



for _ in range(10):
    
    # i just bomb it with messages
    # surely it won't drop
    for cmd in wanted:

        request = connection.mav.command_long_encode(
                connection.target_system,  # Target system ID
                connection.target_component,  # Target component ID
                mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL,  # ID of command to send
                0,  # Confirmation
                cmd,  # param1: Message ID to be streamed
                1000000, # param2: Interval in MICROseconds
                0,       # param3 (unused)
                0,       # param4 (unused)
                0,       # param5 (unused)
                0,       # param5 (unused)
                0        # param6 (unused)
        )

        connection.mav.send(request)

while time.time()-start < TWO_HOURS:
    msg = connection.recv_msg()

    if not msg: continue
    
    # log the messages
    # AHDKFHDASFHJGDSHJAGFHJDSJAAAH
    
    all_message.write(msg + "\n\n--------------------\n\n")