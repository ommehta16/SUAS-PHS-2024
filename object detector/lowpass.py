import numpy as np
import math
from multiprocessing import Pool

def halftone(img:np.ndarray, threshold:int) -> np.ndarray:
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            if (img[i,j].sum()/3 < threshold): img[i,j]*=0
            else: img[i,j] = 255
    return img

if __name__ == "__main__":
    from img_io import *
    import time
    img_arr = img_to_arr(open_img("object detector/cat.jpeg"))
    
    start = time.time()
    new_img_arr = halftone(img_arr,200)
    end = time.time()
    
    arr_to_img(new_img_arr).save("cat2.jpeg")
    print(str(end-start) + " seconds")