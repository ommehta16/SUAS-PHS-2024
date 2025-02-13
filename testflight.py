from pymavlink import mavutil, mavwp
import time
import math

# https://ardupilot.org/dev/docs/raspberry-pi-via-mavlink.html
# 
# 
# @allanchen1 ^^ check for hardware stuff
# 
# 
# Try to run missionplanner on pi if you can
# but otherwise its chill

CONNECTIONPORT = '/dev/serial0'

connection = mavutil.mavlink_connection(CONNECTIONPORT,baud=57600)

connection.wait_heartbeat()

file = open("LOG.txt","a+")

while True:
    msg = connection.recv_msg()

    if msg:
        file.write(msg + "\n\n--------------------\n\n")