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
    