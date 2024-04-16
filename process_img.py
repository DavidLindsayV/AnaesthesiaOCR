import tempfile
from PIL import Image, ImageEnhance, ImageFilter

import os

import cv2
import numpy as np
from PIL import Image
from deskew import determine_skew
from typing import Tuple, Union
import math

def normalise(img):
    norm_img = np.zeros((img.shape[0], img.shape[1]))
    img = cv2.normalize(img, norm_img, 0, 255, cv2.NORM_MINMAX)
    return img

def remove_noise(image):
    return cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 15)


def thresholding(image, percent):
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(image)
    # image = cv2.threshold(image, thresh, 255, cv2.THRESH_BINARY)[1]
    # image = cv2.threshold(image, min_val + (max_val-min_val)*percent, 255, cv2.THRESH_BINARY)[1]
    # return image
    return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU) [1]

def flipGreyscale(image):
    return cv2.bitwise_not(image)

def set_image_dpi(image):
    im = cv2_to_pil(image)
    length_x, width_y = im.size
    factor = min(1, float(1024.0 / length_x))
    size = int(factor * length_x), int(factor * width_y)
    im_resized = im.resize(size, Image.LANCZOS)
    return pil_to_opencv(im_resized)


def resize_height(image, ideal_height):
    return image.resize((int(image.width/image.height * ideal_height), ideal_height))

def rotate(
        image: np.ndarray, angle: float, background: Union[int, Tuple[int, int, int]]
) -> np.ndarray:
    old_width, old_height = image.shape[:2]
    angle_radian = math.radians(angle)
    width = abs(np.sin(angle_radian) * old_height) + abs(np.cos(angle_radian) * old_width)
    height = abs(np.sin(angle_radian) * old_width) + abs(np.cos(angle_radian) * old_height)

    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    rot_mat[1, 2] += (width - old_width) / 2
    rot_mat[0, 2] += (height - old_height) / 2
    return cv2.warpAffine(image, rot_mat, (int(round(height)), int(round(width))), borderValue=background)


def pil_to_opencv(pil_image):
    numpy_image = np.array(pil_image)
    opencv_image = cv2.cvtColor(numpy_image, cv2.COLOR_RGB2BGR)
    return opencv_image

def cv2_to_pil(cv2_image):
    cv2_image_rgb = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(cv2_image_rgb)
    return pil_image

def get_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

def enhanceContrast(img, factor):
    img = cv2_to_pil(img)
    contrast_enhancer = ImageEnhance.Contrast(img)
    img = contrast_enhancer.enhance(factor) 
    return pil_to_opencv(img)
        
def enhanceSharpness(img, factor):
    img = cv2_to_pil(img)
    sharpness_enhancer = ImageEnhance.Sharpness(img)
    img = sharpness_enhancer.enhance(factor)  
    img = pil_to_opencv(img)
    return img

def despeckle_image(img, kernel_size, iterations):
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    img = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel, iterations=iterations)
    return img

def colorThresholding(image):
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_color = np.array([0, 50, 100])    # Lower threshold for the target color (you can adjust these values)
    upper_color = np.array([255, 255, 255])  # Upper threshold for the target color (you can adjust these values)
    mask = cv2.inRange(hsv_image, lower_color, upper_color)
    imask = mask>0
    masked = np.zeros_like(image, np.uint8)
    masked[imask] = image[imask]
    return masked

def get_parameter_imgs(modified_image):
    #parameters = 
    # rtime	ecg.hr	ecg.st1	ecg.st2	ecg.st3	ecg.imp_rr	p1.sys	p1.dia	p1.mean	p1.hr	p2.sys	p2.dia	p2.mean	p2.hr	p3.sys	p3.dia	p3.mean	p3.hr	p4.sys	p4.dia	p4.mean	p4.hr	nibp.sys	nibp.dia	nibp.mean	nibp.hr	t1.temp	t2.temp	t3.temp	t4.temp	spo2.SpO2	spo2.pr	spo2.ir_amp	co2.et	co2.fi	co2.rr	co2.amb_press	o2.et	o2.fi	n2o.et	n2o.fi	aa.et	aa.fi	aa.mac_sum	p5.sys	p5.dia	p5.mean	p5.hr	p6.sys	p6.dia	p6.mean	p6.hr

    #Get a subsection that is the heart rate
    heartrate_image = modified_image.crop((500, 160, 580, 230))  #TODO ask Michael how many digits each of these can be, and whether the number of digits changes their positions
    #ecto2
    ecto2_image = modified_image.crop((465, 330, 510, 365))
    #fico2
    fico2_image = modified_image.crop((450, 365, 500, 390)) 
    #rr
    rr_image = modified_image.crop((500, 360, 530, 390)) 
    #systolic pressure
    sys_psi_image = modified_image.crop((410, 400, 470, 430)) 
    #diastolic pressure
    dias_psi_image = modified_image.crop((480, 400, 530, 430)) 
    #arterial pressure
    art_psi_image = modified_image.crop((423, 430, 460, 450)) 
    #anaes concentration 1
    ana_conc1_image = modified_image.crop((115, 400, 160, 425)) 
    # anaes concentration 2  
    ana_conc2_image = modified_image.crop((120, 425, 160, 445)) 

    imageDict = {'ecg.hr':heartrate_image, 'co2.et':ecto2_image, 'co2.fi':fico2_image, 'co2.rr':rr_image, 'p1.sys':sys_psi_image, 'p1.dia':dias_psi_image, 'p1.mean':art_psi_image, 'aa.et': ana_conc1_image, 'aa.fi': ana_conc2_image}

    ideal_height = 100

    for filename in os.listdir("processed_images"):
        os.remove(os.path.join("processed_images", filename))
    modified_image.save(os.path.join("processed_images", "Img.png"))
    for key in imageDict.keys():
        img = imageDict[key]
        img = resize_height(img, ideal_height)
        img = pil_to_opencv(img)
        img = set_image_dpi(img)
        # img = remove_noise(img)
        img = enhanceContrast(img, 3)
        
        # img = despeckle_image(img, 5, 1)
        # img = enhanceSharpness(img, 2)
        
        # img = colorThresholding(img)
        img = get_grayscale(img)
        # img = thresholding(img, 0.6)
        # img = flipGreyscale(img)
        # img = normalise(img)

        #Save the images
        img = cv2_to_pil(img)
        imageDict[key] = img
        imageDict[key].save(os.path.join("processed_images", key + "-img.png"))

    return imageDict
    


def process_img(imgName):
    image = Image.open(imgName)

    #Get image in the right orientation
    modified_image = image.transpose(Image.FLIP_TOP_BOTTOM)
    modified_image = modified_image.transpose(Image.FLIP_LEFT_RIGHT)
    modified_image = pil_to_opencv(modified_image)
    # modified_image = normalise(modified_image)
    # modified_image = deskew(modified_image) TODO deskew the image keystone correction
    modified_image = cv2_to_pil(modified_image)

    #Denoise image
    # open_cv_image = numpy.array(modified_image)
    # modified_image = cv2.fastNlMeansDenoisingColored(open_cv_image)  #this denoising did nothing. But this function can take extra arguments so maybe denoising can be improved
    # modified_image = Image.fromarray(open_cv_image)

    #Make image greyscale 
    # modified_image = modified_image.convert('L')

    imgs = get_parameter_imgs(modified_image)
    return imgs
    # return None


#TO TRY:
# - keystone correction
# - image despecling
# - better AI