from pymavlink import mavutil, mavwp
import time
import math
from plane import Plane


#mavwp --> waypoints

CONNECTIONPORT = 'udpin:localhost:14540'
# mavlink simulator ^

# CONNECTIONPORT = '/dev/ttyAMA0'
# when running this on the rpi ^

connection = mavutil.mavlink_connection(CONNECTIONPORT,baud=57600)

connection.wait_heartbeat()

susser = Plane(connection)

print(f"Heartbeat recieved from {connection.target_system} via {connection.target_component}")

msg = connection.recv_msg()

if msg:
    print(msg)

lat:int = -1 # degE7
lon:int = -1 # degE7
# latitude and longitude are in degrees :(
# sadly, the earth is round
# this makes our job much harder
alt:int = -1 # mm
rel_alt:int = -1 # mm

vel = [0,0,0]

'''
!!!

docs are in /mavlink/message_definitions/v1.0/common.xml

!!!
'''
# bro
# i genuinely hate whoever wrote up this standard
# 
# https://mavlink.io/en/mavgen_python/
# https://mavlink.io/en/messages/common.html
# 
# it's so good
# BUT WHY TF
# DO I HAVE TO SCAN THRU AN XML FOR FUCDJSLHFKDING DOCS
# LIKE WTF BRO
# FJDLSAHJFKLSHDFKJLHAHSDJKFASDGFHKSDFKGASDHJFGADHJS


while True:
    try:
        lat = connection.messages['GLOBAL_POSITION_INT'].lat
        lon = connection.messages['GLOBAL_POSITION_INT'].long
        alt = connection.messages['GLOBAL_POSITION_INT'].alt

        vel = [
            connection.messages['GLOBAL_POSITION_INT'].vx,
            connection.messages['GLOBAL_POSITION_INT'].vy,
            connection.messages['GLOBAL_POSITION_INT'].vz,
               ]
        alt = connection.messages['GLOBAL_POSITION_INT'].alt
        rel_alt = connection.messages['GLOBAL_POSITION_INT'].relative_alt
        timestamp = connection.time_since('GLOBAL_POSITION_INT')
    except:
        try: 
            lat = connection.messages['GPS_RAW_INT'].lat
            lon = connection.messages['GPS_RAW_INT'].lon
            alt = connection.messages['GPS_RAW_INT'].alt
            cog = connection.messages['GPS_RAW_INT'].alt # direction that moving over ground


            rel_alt = connection.messages['GPS_RAW_INT'].relative_alt
            timestamp = connection.time_since('GPS_RAW_INT')
        except:
            print('lol where tf even are we')

    time.sleep(0.5)