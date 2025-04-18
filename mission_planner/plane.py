'''
Definition of Plane, an object that stores all info about the plane
'''

from pymavlink import mavutil, mavwp
import time
import math

class Plane:
    def __init__(self,master):
        '''
        Initialize with mavlink connection _master_
        '''
        self.vel = [0,0,0]
        '''
        [x, y, z]
        
        positive is north/east/down respectively
        '''

        self.loc = [0,0]
        '''
        [lat,long]

        (the earth's a sphere apparently?)
        '''

        self.alt = 0
        self.rel_alt = 0
        self.master = master

        # SET OTHER PROPS HERE
    
    def takeoff(self):
        ALT_TO = 20 # in meters
        self.master.mav.command_takeoff_send(
            self.master.target_system,  # Target system ID
            self.master.target_component, # Target component ID
            0,                  # Do not use takeoff yaw
            0,                  # Latitude (not used for takeoff)
            0,                  # Longitude (not used for takeoff)
            ALT_TO,             # Altitude to takeoff to (in meters)
            0, 0, 0             # Empty params for takeoff
        )

        reached_altitude = False
        start=time.time()
        while not reached_altitude and time.time() > start + 5*60:
            self.update_pos()
            print(f"Current altitude: {self.alt} meters")
            if self.alt >= ALT_TO * 0.95: # Check if close to target
                reached_altitude = True
                print("reached takeoff altitude")
        if not reached_altitude:
            raise TimeoutError("didn't reach takeoff target altitude in time")

        # plane should loiter until sent flight plan up
        mode = 'LOITER'
        mode_id = self.master.mode_mapping()[mode]
        self.master.mav.set_mode_send(
            self.master.target_system,
            mavutil.mavlink.MAV_MODE_CUSTOM_MODE,
            mode_id
        )
        print(f"Transitioned to {mode} mode.")

    def update_pos(self) -> bool:
        '''
        Pull current position from mavlink

        returns whether the position changed, **NOT** success/failure
        '''
        try:
            new_pos = self.master.messages['GLOBAL_POSITION_INT']
            if self.pos == [new_pos.lat, new_pos.long] and self.alt==new_pos.alt and self.vel == [new_pos.vx, new_pos.vy, new_pos.vz] and self.alt == new_pos.alt and self.rel_alt == new_pos.relative_alt: return False
            
            lat = new_pos.lat
            lon = new_pos.long
            self.pos = [lat,lon]
            self.alt = new_pos.alt

            self.vel = [
                new_pos.vx,
                new_pos.vy,
                new_pos.vz,
            ]

            self.alt = new_pos.alt
            self.rel_alt = new_pos.relative_alt
            return True
        except:
            try:
                new_pos = self.master.messages['GPS_RAW_INT']
                if self.pos == [new_pos.lat, new_pos.long] and self.alt==new_pos.alt and self.vel == [math.sin(cog) * v, math.cos(cog) * v, self.vel[2]]  and self.rel_alt == new_pos.relative_alt: return False
                self.lat = new_pos.lat
                self.lon = new_pos.lon
                self.alt = new_pos.alt
                cog = new_pos.cog
                v = new_pos.vel

                self.vel = [
                    math.sin(cog) * v,
                    math.cos(cog) * v,
                    self.vel[2] # keep or throw?
                ]


                self.rel_alt = new_pos.relative_alt
                return True
            except:
                print('lol where tf even are we buhhhhh')
                return False
    