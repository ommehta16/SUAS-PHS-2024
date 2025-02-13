from pymavlink import mavutil, mavwp
import time
import math

# https://ardupilot.org/dev/docs/raspberry-pi-via-mavlink.html
# 
# 
# @allanchen1 ^^ check for hardware stuff
# you should be able to just connect to TELEM1 though and turn on pixhawk



# @PhantomFrenzy151 imma need you to do the setup on the pi
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

file = open("LOG.txt","a+")

start = time.time()

TWO_HOURS = 2 * 60 * 60

while time.time()-start < TWO_HOURS:
    msg = connection.recv_msg()

    if msg:
        file.write(msg + "\n\n--------------------\n\n")