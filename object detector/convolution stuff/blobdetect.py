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
    percentCover = 0
    maxPercent = 10
    imgCusp = 10
    dAspRat = 2
    rad = 3
    inp_img_fp = "road.jpg"
    # out_img_fp= "test3.jpg"

    screen = pygame.display.set_mode(size)
    pygame.font.init()
    clock = pygame.time.Clock()
    
    img:np.ndarray = img_io.img_to_arr(img_io.open_img(inp_img_fp))
    
    img = np.clip(img + convolute.EdgeDetect.sobel(img),0,255)
    img = lowpass.halftone(img,200)

    chl = np.pad(img[20:-20,20:-20,0],(20,20),"constant",constant_values=(0,0))
    overlay = np.zeros(img.shape,int)

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
                overlay[cX,cY,(x+y)%3] += 127
                overlay[cX,cY,int(((x+y)%9)/3)] += 64
                overlay[cX,cY,int(((x+y)%27)/9)] += 32
                overlay[cX,cY,int(((x+y)%81)/27)] += 16
                overlay[cX,cY,int(((x+y)%243)/81)] += 8
                l = min(l,cX)
                r = max(r,cX)
                t = min(t,cY)
                b = max(b,cY)
                for i in range(-rad,rad+1):
                    for j in range(-rad,rad+1):
                        if ((not (cX+i,cY+j) in visited) and cX > 20 and cX < chl.shape[0]-21 and cY > 20 and cY < chl.shape[1]-21 and chl[cX+i,cY+j] >= imgCusp):
                            visited.add((cX+i,cY+j))
                            toVisit.append((cX+i,cY+j))
            if (b == t or l == r): continue
            boundingBoxes.append(((b-t)*(r-l),t,l,b-t,r-l))
    print(boundingBoxes)


    for c in range(3):
        img[:,:,c] = chl
    img = np.clip(img+overlay,0,255)
    img_surf = img_io.pil_to_pyg(img_io.arr_to_img(img))
    boundingBoxes.sort()

    drawn = 0
    for i in range(1,len(boundingBoxes)):
        box = boundingBoxes[-i]
        if (box[0] < percentCover*chl.size/100 or box[0] > maxPercent*chl.size/100): continue
        if (float(box[4])/box[3] > dAspRat or float(box[4])/box[3] < 1/dAspRat): continue
        pygame.draw.rect(img_surf,"red",pygame.rect.Rect(box[1],box[2],box[3],box[4]),2)
        drawn += 1
        if drawn >= 3: break
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