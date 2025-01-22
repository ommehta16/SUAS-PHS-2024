import img_io
from PIL import Image
import numpy as np
import math
import sys
import time
import pygame
import convolute
import multiprocessing as mp
import lowpass
from collections import deque


def main():
    pygame.init()
    size = width, height = 800, 600

    screen = pygame.display.set_mode(size)
    pygame.font.init()

    clock = pygame.time.Clock()

    img:np.ndarray = img_io.img_to_arr(img_io.open_img("test.png"))
    # img = convolute.Blur.gaussian(img,10,15)

    img = convolute.EdgeDetect.dog(img,15,16,10)
    img = lowpass.halftone(img,50)

    chl = np.pad(img[20:-20,20:-20,0],(20,20),"constant",constant_values=(0,0))
    
    x = 20
    y = 20

    visited = set()
    toVisit = deque()
    boundingBoxes = []
    print(chl.shape[0])
    while (x<chl.shape[0]-20):
        while(y<chl.shape[1]-20):
            if (chl[x,y] != 0): print("a")
            if (chl[x,y] != 1):
                y+=1
                continue
            l = x
            r = x
            t = y
            b = y

            toVisit.append((x,y))
            visited.add((x,y))
            while(len(toVisit)):
                cX,cY = toVisit.pop()

                if ((not ((cX-1,cY) in visited)) and cX>20 and chl[cX-1,cY] == 1):
                    visited.add((cX-1,cY))
                    toVisit.append((cX-1,cY))
                    l = min(l,cX)
                if ((not ((cX+1,cY) in visited)) and cX<chl.shape[0]-21 and chl[cX+1,cY] == 1):
                    visited.add((cX+1,cY))
                    toVisit.append((cX+1,cY))
                    r = max(r,cX)
                if ((not ((cX,cY-1) in visited)) and cY>20 and chl[cX,cY-1] == 1):
                    visited.add((cX,cY-1))
                    toVisit.append((cX,cY-1))
                    t = min(t,cY)
                if ((not ((cX,cY+1) in visited)) and cY<chl.shape[1]-21 and chl[cX,cY+1] == 1):
                    visited.add((cX,cY+1))
                    toVisit.append((cX,cY+1))
                    b = max(b,cY)
            boundingBoxes.append((l,r,t,b))
            y+=1
        print()
        y=0
        x+=1
    print(boundingBoxes)


    for c in range(3):
        img[:,:,c] = chl
    img_surf = img_io.pil_to_pyg(img_io.arr_to_img(img))
    img_surf = pygame.transform.scale(img_surf,(width,int(img_surf.get_size()[1]/img_surf.get_size()[0] * width)))

    while True:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
        screen.fill("gray")
        screen.blit(img_surf,(0,0))
        pygame.display.update()
        # render stuff here

if __name__ == "__main__": main()