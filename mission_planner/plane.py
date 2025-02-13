from pymavlink import mavutil, mavwp
import time
import math

class Plane:
    
    
    
    def __init__(self,connection:mavutil.mavtcp|mavutil.mavtcpin|mavutil.mavudp|mavutil.mavwebsocket|mavutil.mavmcast|mavutil.DFReader_binary|mavutil.CSVReader|mavutil.DFReader_text|mavutil.mavchildexec|mavutil.mavmmaplog|mavutil.mavlogfile|mavutil.mavserial):
        self.vel = [0,0,0]
        '''
        [x, y, z]
        positive is north/east/down respectively
        '''

        self.loc = [0,0]
        '''
        [lat,long]
        idk how these work
        the earth's a sphere apparently?
        '''

        self.alt = 0
        self.rel_alt = 0
        self.connection = connection


    def update_pos(self) -> None:
        try:
            
            
            lat = self.connection.messages['GLOBAL_POSITION_INT'].lat
            lon = self.connection.messages['GLOBAL_POSITION_INT'].long
            self.pos = [lat,lon]
            self.alt = self.connection.messages['GLOBAL_POSITION_INT'].alt

            self.vel = [
                self.connection.messages['GLOBAL_POSITION_INT'].vx,
                self.connection.messages['GLOBAL_POSITION_INT'].vy,
                self.connection.messages['GLOBAL_POSITION_INT'].vz,
            ]

            self.alt = self.connection.messages['GLOBAL_POSITION_INT'].alt
            self.rel_alt = self.connection.messages['GLOBAL_POSITION_INT'].relative_alt
        except:
            try: 
                self.lat = self.connection.messages['GPS_RAW_INT'].lat
                self.lon = self.connection.messages['GPS_RAW_INT'].lon
                self.alt = self.connection.messages['GPS_RAW_INT'].alt
                cog = self.connection.messages['GPS_RAW_INT'].cog # direction that moving over ground
                v = self.connection.messages['GPS_RAW_INT'].vel

                # DO EPIC TRIG HERE

                self.vel = [
                    math.sin(cog) * v,
                    math.cos(cog) * v,
                    0
                ]


                self.rel_alt = self.connection.messages['GPS_RAW_INT'].relative_alt
            except:
                print('lol where tf even are we buhhhhh')