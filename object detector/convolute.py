import numpy as np
import math
from multiprocessing import Pool

def conv_1_chnl(chl:np.ndarray,conv:np.ndarray) -> np.ndarray:
    '''
    Convolute one channel using the filter `conv`
    '''
    conv_x = conv.shape[1]
    conv_y = conv.shape[0]
    
    new_chl = np.zeros(chl.shape).astype(int)
    chl = np.pad(chl,(conv_y//2,conv_x//2),'constant',constant_values=(0,0))
    
    for y in range(new_chl.shape[0]): # When convoluting on the CPU, this setup is (almost??) unavoidable. GPU access in python w/o CUDA is annoying though
        for x in range(new_chl.shape[1]):
            curr_block = chl[y:y+conv_y,x:x+conv_x]
            new_chl[y,x] = np.multiply(curr_block,conv).sum()
    
    new_chl = new_chl.clip(0,255)
    return new_chl

def convolute(img_arr: np.ndarray,conv: np.ndarray) -> np.ndarray:
    '''
    Apply the convolution filter `conv` to the entire 3-channel image `img_arr`
    '''
    new_img = np.zeros(img_arr.shape).astype(int)
    # mp = ~33% speed improvement on convolution
    with Pool() as pool: # run one process for each channel --> speed improvement BUT has to stitch at the end
        chnl_list = pool.starmap(conv_1_chnl,[(img_arr[:,:,i],conv) for i in range(3)])
    for i in range(3):
        new_img[:,:,i] = chnl_list[i] 

    return new_img

class Blur:
    @staticmethod
    def generate_gauss_kernel(rad,sigma) -> np.ndarray:
        '''Generate a gaussian blur kernel with the specified radius (`rad`) and standard deviation (`sigma`)'''
        arr = np.zeros((2*rad+1,2*rad+1))
        inv_sigma = 1/sigma
        d_squared = lambda x,y: x**2 + y**2
        G = lambda x,y: 0.159154943 * inv_sigma * math.exp(-0.5 * inv_sigma * d_squared(x-rad,y-rad)) # Gaussian function: math from https://en.wikipedia.org/wiki/Gaussian_function
        for y in range(2*rad+1): # loop over the kernel size, set each pixel
            for x in range(2*rad+1):
                arr[x,y] = G(x,y)
                
        return arr/arr.sum()

    @staticmethod
    def gaussian(img: np.ndarray,radius:float,sigma:float) -> np.ndarray:
        '''Apply a gaussian filter on the specified image (`img`) with the specified radius (`rad`) and standard deviation (`sigma`)'''
        img = convolute(img,Blur.generate_gauss_kernel(radius,sigma)) # Convolute using the gaussian filter
        return img
    
    def box(img: np.ndarray, size:float) -> np.ndarray:
        '''Apply a box blur on the specified image (`img`) with the size `size`'''
        def generate_kernel() -> np.ndarray:
            arr = np.zeros((size*2+1,size*2+1))
            arr.fill(1)
            arr = arr * 1/(size*2+1)**2
            return arr
        
        img = convolute(img,generate_kernel())
        
        return img
    
    
class EdgeDetect:
    @staticmethod
    def dog(img: np.ndarray,r1:float,r2:float,prominence:float) -> np.ndarray:
        '''Apply the difference of gaussians to an image: `r1` > `r2`, `prominence` is a scalar applied to the DOG filter'''
        flt = prominence*20*(Blur.generate_gauss_kernel(32,r1)-Blur.generate_gauss_kernel(32,r2)) # DoG => use the difference of two gaussian filters as the convolution filter
        
        tmp = np.clip(conv_1_chnl(0.3 * img[:,:,0] + 0.59*img[:,:,1] + 0.11*img[:,:,2],flt),0,255)
        for c in range(3): img[:,:,c] = tmp #np.clip(conv_1_chnl(img[:,:,c],flt),0,255)
        return img
    def sobel(img: np.ndarray) -> np.ndarray:
        # sobel operator is so nice :)
        fltx = np.array(
            [[1, 0, -1],
            [2,0,-2],
            [1,0,-1]]
        )
        flty = np.array(
            [
                [1,2,1],
                [0,0,0],
                [-1,-2,-1]
            ]
        )
        x = convolute(img,fltx)
        y = convolute(img,flty)
        tmp = np.ndarray(img.shape[:2]).astype(int)
        for i in range(x.shape[0]):
            for j in range(x.shape[1]):
                tmp[i,j] = ((x[i,j][0]*.3 + x[i,j][1]*.59 + x[i,j][0]*.11)**2 + (y[i,j][0]*.3 + y[i,j][1]*.59 + y[i,j][0]*.11)**2)**0.5
        for c in range(3): img[:,:,c] = tmp
        return np.clip(img,0,255)

# Takes 36.110 seconds -- That's SLOW
if __name__ == "__main__":
    from img_io import *
    import time
    img_arr = img_to_arr(open_img("test.png"))
    
    start = time.time()
    new_img_arr = EdgeDetect.sobel(img_arr)
    new_img_arr_1 = EdgeDetect.dog(img_arr,2.25,2,4)
    end = time.time()
    
    arr_to_img(new_img_arr).save("test1.png")
    arr_to_img(new_img_arr_1).save("test2.png")
    print(str(end-start) + " seconds")