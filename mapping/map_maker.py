import numpy as np
from PIL import Image
import multiprocessing as mp
import multiprocessing.connection
import time

def develop_map(conn:multiprocessing.connection.Connection):
    running = True
    while True:
        # simple plumbing work :)
        while conn.poll():
            newData = conn.recv()

            if type(newData) == str:
                if newData == "stop":
                    running = False
                    break
            elif type(newData) == int:
                ...
            else:
                ...



def make_map(images:np.ndarray[Image.Image], coords:np.ndarray, imgSize:tuple[float,float]) -> np.array:
    '''
    `images` is an array of PIL Images of length n

    `transformations` is a 2D array with dimensions n by 3; coords[i] is in the form [latitude, longitude, rotation=hdg]

    `imgSize` is the dimensions of the area that the camera scans. Should be suaser-aligned (i.e. imgSize[0] is the width respective to plane)
    
    
    returns the result of all images composited together
    '''
    
    # this function should layer all of the images together, transformed by their respective transformations.

    # How hard this is really depends on how accurate GPS is
    # we can increase GPS accuracy by just adding another external unit and asking the pixhawk to average them all together

    # If GPS accuracy isn't enough, we can use ground features and the GPS "hint" to pull it together
    # So detect contours, rectangle-ify them, and try to align near rectangles as best as possible (binary search position :| )

    # lets set some ground rules:
    #  - transform as rotate (about center) --> translate
    #  - the result should be a RECTANGLE with ALL pixels filled in

    # To deal with pixels shared by two images, we have a few options:
    #  - average them
    #  - blur across the edges of shared area
    #  - pick randomly
    #  - use first value

    # I'm not sure if mp would make this go faster
    # like we could give each thread a color channel to do
    # but idk

    locations = locateImages(images,coords,imgSize) # need to actually calculate this

    final_img = composite(images, locations)
    
    return images[0]

def locateImages(images: np.ndarray[Image.Image],coords:np.ndarray,imgSize:tuple[float,float]) -> np.ndarray:
    '''
    `images` is an array of PIL Images of length n

    `coords` is a 2D array with dimensions n by 3; coords[i] is in the form [latitude, longitude, rotation=hdg]

    `imgSize` is the dimensions of the area that the camera scans. Should be suaser-aligned (i.e. imgSize[0] is the width respective to plane)
     
    
    returns the positions and rotations that the images should go in (position in pixels from bottom left)
    '''
    # work from bottom left
    # place images s.t. feature bounding areas line up (use circles --> radius to get vibe)
    # don't actually paste the images down yet tho

    return np.array()

def composite(images:np.ndarray[Image.Image],locations:np.ndarray) -> np.ndarray:
    '''
    `images` is an array of PIL Images with length n

    `locations` is a 2D array of size n, 3: locations[i] = [x position, y position, rotation]


    returns 1 image of whole array but composited
    '''

    return np.array()
