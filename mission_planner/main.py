from pymavlink import mavutil, mavwp
import time
import math
from plane import Plane

'''
STATE aS OF 2/18
works on simulator, but idk if works on plane

'''

CONNECTIONPORT = 'udpin:localhost:14540'
# mavlink simulator ^

# CONNECTIONPORT = '/dev/serial0'
# for final deployment ^

# CONNECTIONPORT = '/dev/ttyAMA0'
# or this maybe? idk ^

connection = mavutil.mavlink_connection(CONNECTIONPORT,baud=57600)

connection.wait_heartbeat()

susser = Plane(connection)

print(f"Heartbeat recieved from {connection.target_system} via {connection.target_component}")

''' docs are in /mavlink/message_definitions/v1.0/common.xml '''

# i genuinely hate whoever wrote up this standard
# 
# https://mavlink.io/en/mavgen_python/
# https://mavlink.io/en/messages/common.html

# FJDLSAHJFKLSHDFKJLHAHSDJKFASDGFHKSDFKGASDHJFGADHJS


while True:
    time.sleep(0.5)
    susser.update_pos()

    # send a heartbeat periodically

    # we should try to mp this
    # would make speedy
    # and less blocking
    # but idk how

    # OR just do normal async/await
    # but idk how that as well

    # FHDKASHFKJHDSJKAHFKJDHGAFJAKSDJKFGJKASDGJFHKGDSJ PYTHON ADJHFKASGHFJDKGFJGSHJKFGJASKFGJh