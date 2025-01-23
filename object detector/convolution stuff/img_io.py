from PIL import Image
import numpy as np
import pygame

def img_to_arr(image:Image.Image) -> np.ndarray:
    img = np.array(image).astype(int)
    if img.shape[2] > 3:
        img = img[:,:,:3]
    return img

def arr_to_img(image_array:np.ndarray) -> Image.Image :
    return Image.fromarray(np.clip(image_array,0,255).astype(np.uint8))

def open_img(file_name:str) -> Image.Image :
    return Image.open(file_name,"r")

def save_img(image:Image.Image, file_name:str) -> None:
    image.save(file_name)

def pil_to_pyg(image:Image.Image) -> pygame.Surface:
    return pygame.image.fromstring(image.tobytes(),image.size,image.mode).convert()