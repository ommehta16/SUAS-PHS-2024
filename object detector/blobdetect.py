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
    percentCover = 0.07
    imgCusp = 25
    dAspRat = 0.5

    screen = pygame.display.set_mode(size)
    pygame.font.init()

    clock = pygame.time.Clock()

    img:np.ndarray = img_io.img_to_arr(img_io.open_img("box2.jpeg"))
    # img = convolute.Blur.gaussian(img,10,15)

    img = convolute.EdgeDetect.dog(img,199,200,90)
    # img = lowpass.halftone(img,10)

    chl = np.pad(img[20:-20,20:-20,0],(20,20),"constant",constant_values=(0,0))
    
    x = 20
    y = 20

    visited = set()
    toVisit = deque()
    boundingBoxes = []
    for x in range(20,chl.shape[0]-20):
        for y in range(20,chl.shape[1]-20):
            if (chl[x,y] < imgCusp or (x,y) in visited):
                continue
            l = x
            r = x
            t = y
            b = y

            toVisit.append((x,y))
            visited.add((x,y))
            while(len(toVisit)):
                cX,cY = toVisit.pop()

                if ((not ((cX-1,cY) in visited)) and cX>20 and chl[cX-1,cY] >= imgCusp):
                    visited.add((cX-1,cY))
                    toVisit.append((cX-1,cY))
                    l = min(l,cX)
                if ((not ((cX+1,cY) in visited)) and cX<chl.shape[0]-21 and chl[cX+1,cY] >= imgCusp):
                    visited.add((cX+1,cY))
                    toVisit.append((cX+1,cY))
                    r = max(r,cX)
                if ((not ((cX,cY-1) in visited)) and cY>20 and chl[cX,cY-1] >= imgCusp):
                    visited.add((cX,cY-1))
                    toVisit.append((cX,cY-1))
                    t = min(t,cY)
                if ((not ((cX,cY+1) in visited)) and cY<chl.shape[1]-21 and chl[cX,cY+1] >= imgCusp):
                    visited.add((cX,cY+1))
                    toVisit.append((cX,cY+1))
                    b = max(b,cY)
            boundingBoxes.append(((b-t)*(r-l),t,l,b-t,r-l))
    print(boundingBoxes)


    for c in range(3):
        img[:,:,c] = chl
    img_surf = img_io.pil_to_pyg(img_io.arr_to_img(img))
    boundingBoxes.sort()
    for i in range(1,min(5,len(boundingBoxes)-1)):
        box = boundingBoxes[i*-1]
        if (box[0] < percentCover*chl.size/100): continue
        if (abs(float(box[4])/box[3]-1) > dAspRat): continue
        pygame.draw.rect(img_surf,"red",pygame.rect.Rect(box[1],box[2],box[3],box[4]),2)
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