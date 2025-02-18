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

all_message = open("LOG.txt","+a")
vlt_log = open("VOLTAGE", "+ab")

start = time.time()

TWO_HOURS = 2 * 60 * 60

wanted = [
    mavutil.mavlink.GPS_RAW_INT,
    mavutil.mavlink.RAW_PRESSURE,
    mavutil.mavlink.ATTITUDE,
    mavutil.mavlink.SCALED_PRESSURE,
    mavutil.mavlink.GLOBAL_POSITION_INT,
    # mavutil.mavlink.SYS_STATUS,
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
                1e6, # param2: Interval in MICROseconds
                0,       # param3 (unused)
                0,       # param4 (unused)
                0,       # param5 (unused)
                0,       # param5 (unused)
                0        # param6 (unused)
        )

        connection.mav.send(request)
    
for _ in range(10): # bomb with requests for system status at 100Hz
    request = connection.mav.command_long_encode(
            connection.target_system,  # Target system ID
            connection.target_component,  # Target component ID
            mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL,  # ID of command to send
            0,  # Confirmation
            mavutil.mavlink.SYS_STATUS,  # param1: Message ID to be streamed
            1e4, # param2: Interval in MICROseconds
            0,       # param3 (unused)
            0,       # param4 (unused)
            0,       # param5 (unused)
            0,       # param5 (unused)
            0        # param6 (unused)
    )

    connection.mav.send(request)

volts = 0

TIME_BASE = 0

while time.time()-start < TWO_HOURS:
    msg = connection.recv_msg()
    if not msg: continue
    if TIME_BASE == 0: TIME_BASE = msg.timestamp
    # log the messages
    # AHDKFHDASFHJGDSHJAGFHJDSJAAAH

    if msg.get_type() == mavutil.mavlink.SYS_STATUS:
        try:
            tmp = msg.voltage_battery

            if (abs(tmp-volts) >= 1):
                volts = tmp
                curr_time = msg.timestamp-TIME_BASE
                vlt_log.write(curr_time.to_bytes(64,'big'))
                vlt_log.write(volts.to_bytes(64,'big'))
        except: pass
    
    all_message.write(msg + "\n\n--------------------\n\n")

def readVolts(fp: str = "VOLTAGE") -> dict:
    '''
    Reads voltage values from the given file (`VOLTAGE` if none specified)

    Outputs a dict that maps from int (timestamp = microseconds since start) to int (voltage = mV)
    '''
    log = open(fp,'rb')

    MAX_SAMPLES = int(7.2e6) # this is if we had 1000Hz for 2 hours... not happening lol
    samples = 0

    voltsAt = {}
    
    while samples < MAX_SAMPLES:
        samples+=1
        tim = log.read(64)
        if tim is None: break
        vlt = log.read(64)
        if vlt is None: break

        try: voltsAt[int.from_bytes(tim,'big')] = int.from_bytes(vlt,'big')
        except: pass
    return voltsAt
