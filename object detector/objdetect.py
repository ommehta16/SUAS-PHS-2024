import numpy as np
import math
import time
import multiprocessing as mp
from matplotlib import pyplot as plt
import cv2
from collections import deque

def main():
    inp_img_fp = "road.jpg"

    img = cv2.imread(inp_img_fp,1)

    rn = time.time()
    img2 = np.array(cv2.Canny(img,250,500))

    visited = set()
    toVisit = deque()
    boundingBoxes = []
    rad = 3
    for x in range(20,img2.shape[0]-20):
        for y in range(20,img2.shape[1]-20):
            if (img2[x,y] == 0 or (x,y) in visited): continue
            l, r, t, b = x, x, y, y

            toVisit.append((x,y))
            visited.add((x,y))
            while(len(toVisit)):
                cX,cY = toVisit.pop()

                l = min(l,cX)
                r = max(r,cX)
                t = min(t,cY)
                b = max(b,cY)
                for i in range(-rad,rad+1):
                    for j in range(-rad,rad+1):
                        if ((not (cX+i,cY+j) in visited) and cX > 20 and cX < img2.shape[0]-21 and cY > 20 and cY < img2.shape[1]-21 and img2[cX+i,cY+j] != 0):
                            visited.add((cX+i,cY+j))
                            toVisit.append((cX+i,cY+j))
            if (b == t or l == r): continue
            boundingBoxes.append(((b-t)*(r-l),t,l,b,r))
    
    # for c in range(3):
    #     img[:,:,c] = img2
    taken = np.zeros(img2.shape,int)
    boundingBoxes.sort()

    i = len(boundingBoxes)-1
    while (i>=0):
        box = boundingBoxes[i]
        t, l, b, r = box[1:]
        if(taken[l,t] or taken[r,t] or taken[l,b] or taken[r,b]):
            i-=1
            continue
        taken[l-20:r+20,t-20:b+20] = 1
        if (float(box[4]-box[2])/(box[3]-box[1]) < 1/6 or float(box[4]-box[2])/(box[3]-box[1]) > 6): continue
        if (box[0] < img.size * 0.00001 or box[0] > img.size * 0.1): continue
        cv2.rectangle(img,(box[1]-5,box[2]-5),(box[3]+5,box[4]+5),(0,0,255),2)
        i-=1
    print(time.time()-rn)
    img = img[:,:,::-1]
    # print(boundingBoxes)
    plt.imshow(img,interpolation="bicubic")
    plt.xticks([]); plt.yticks([])
    plt.show()
    cv2.imwrite("roadbw.jpg",img)

    # TWO WAYS OF CONTINUING:
    #  - just dfs to find clusters √
    #  - figure out individual object detection in opencv:
    #       https://docs.opencv.org/3.2.0/d7/d8b/tutorial_py_face_detection.html
    #       https://docs.opencv.org/3.2.0/dc/d88/tutorial_traincascade.html
    #
    #       tutorials ^^
    
if __name__ == "__main__": main()