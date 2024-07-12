import tempfile
from PIL import Image, ImageEnhance, ImageFilter

import os

import cv2
import numpy as np
from PIL import Image
from typing import Tuple, Union
import math
from skimage import io, restoration, img_as_ubyte

from query import find_bboxes


def normalise(img):
    norm_img = np.zeros((img.shape[0], img.shape[1]))
    img = cv2.normalize(img, norm_img, 0, 255, cv2.NORM_MINMAX)
    return img


def remove_noise(image):
    # return cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 15)
    return cv2.fastNlMeansDenoisingColored(image)

def bilateral_filter_noseremover(img):
    return cv2.bilateralFilter(img, 9, 75, 75)


def thresholding(image):
    # min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(image)
    # image = cv2.threshold(image, thresh, 255, cv2.THRESH_BINARY)[1]
    # image = cv2.threshold(image, min_val + (max_val-min_val)*percent, 255, cv2.THRESH_BINARY)[1]
    # return image
    return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    # image = cv2.medianBlur(image,5)
    # return cv2.adaptiveThreshold(image,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,21,6)

def flipGreyscale(image):
    return cv2.bitwise_not(image)


def resize_height(image, ideal_height):
    return image.resize((int(image.width / image.height * ideal_height), ideal_height))


def rotate(
    image: np.ndarray, angle: float, background: Union[int, Tuple[int, int, int]]
) -> np.ndarray:
    old_width, old_height = image.shape[:2]
    angle_radian = math.radians(angle)
    width = abs(np.sin(angle_radian) * old_height) + abs(
        np.cos(angle_radian) * old_width
    )
    height = abs(np.sin(angle_radian) * old_width) + abs(
        np.cos(angle_radian) * old_height
    )

    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    rot_mat[1, 2] += (width - old_width) / 2
    rot_mat[0, 2] += (height - old_height) / 2
    return cv2.warpAffine(
        image, rot_mat, (int(round(height)), int(round(width))), borderValue=background
    )


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
    lower_color = np.array(
        [0, 50, 100]
    )  # Lower threshold for the target color (you can adjust these values)
    upper_color = np.array(
        [255, 255, 255]
    )  # Upper threshold for the target color (you can adjust these values)
    mask = cv2.inRange(hsv_image, lower_color, upper_color)
    imask = mask > 0
    masked = np.zeros_like(image, np.uint8)
    masked[imask] = image[imask]
    return masked

def equalizeHist(img):
    return cv2.equalizeHist(img)

def gaussianBlur(img):
    return cv2.GaussianBlur(img, (5, 5), 1)

def size_threshold(bw, minimum, maximum):
    retval, labels, stats, centroids = cv2.connectedComponentsWithStats(bw)
    for val in np.where((stats[:, 4] < minimum) + (stats[:, 4] > maximum))[0]:
      labels[labels==val] = 0
    return (labels > 0).astype(np.uint8) * 255  

def scikit_denoising(img):
    denoised_image = restoration.denoise_tv_chambolle(img, weight=0.1)
    return img_as_ubyte(denoised_image)

def dist_to_bbox(point, bbox):
    px, py = point
    x0, y0, x1, y1 = bbox
    # Ensure the box coordinates are correctly ordered
    x_min, x_max = sorted([x0, x1])
    y_min, y_max = sorted([y0, y1])
        # Calculate the shortest distance to the box
    if px < x_min:
        if py < y_min:
            # Point is to the top-left of the box
            return math.sqrt((x_min - px) ** 2 + (y_min - py) ** 2)
        elif py > y_max:
            # Point is to the bottom-left of the box
            return math.sqrt((x_min - px) ** 2 + (y_max - py) ** 2)
        else:
            # Point is directly to the left of the box
            return x_min - px
    elif px > x_max:
        if py < y_min:
            # Point is to the top-right of the box
            return math.sqrt((x_max - px) ** 2 + (y_min - py) ** 2)
        elif py > y_max:
            # Point is to the bottom-right of the box
            return math.sqrt((x_max - px) ** 2 + (y_max - py) ** 2)
        else:
            # Point is directly to the right of the box
            return px - x_max
    else:
        if py < y_min:
            # Point is directly above the box
            return y_min - py
        else:
            # Point is directly below the box
            return py - y_max

def get_field_cropped_imgs(image, monitor, bbox_adjustment):
    

    fieldpos = monitor.get_field_pos()
    imageDict = {}

    if not bbox_adjustment:
        for key, box in fieldpos.items():
            imageDict[key] = image.crop(box)

    elif bbox_adjustment:
        center_coords = {}
        for key, box in fieldpos.items():
            center_coords[key] = ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2)

        bboxes = find_bboxes(image)

        #how many pixels the position of each field on the screen has shifted. Judged based on how off-centre the ecg.hr box is
        xShift = 0
        yShift = 0
        for bbox in bboxes:
            xmin = bbox.box[0]
            ymin = bbox.box[1]
            xmax = bbox.box[2]
            ymax = bbox.box[3]
            if xmin <= center_coords['ecg.hr'][0] <= xmax and ymin <= center_coords['ecg.hr'][1] <= ymax:
                xCentre = int((xmin + xmax)/2)
                yCentre = int((ymin + ymax)/2)
                xShift = xCentre - center_coords['ecg.hr'][0]
                yShift = yCentre - center_coords['ecg.hr'][1]
        for key, center in center_coords.items():
            center_coords[key] = (center[0] + xShift, center[1] + yShift)

        bestBBox = {}
        for field, coords in center_coords.items():
            for bbox in bboxes:
                xmin = bbox.box[0] 
                ymin = bbox.box[1] 
                xmax = bbox.box[2] 
                ymax = bbox.box[3] 
                if xmin <= coords[0] <= xmax and ymin <= coords[1] <= ymax and dist_to_bbox(coords, bbox.box) < 0.5*(fieldpos[field][3] - fieldpos[field][1]):
                    if not field in bestBBox.keys():
                        bestBBox[field] = bbox.box
                    else:
                        # If the new bbox found is smaller than the previous one found
                        if (xmax - xmin) * (ymax - ymin) < (
                            bestBBox[field][2] - bestBBox[field][0]
                        ) * (bestBBox[field][3] - bestBBox[field][1]):
                            bestBBox[field] = bbox.box

        for field in fieldpos.keys():
            if not field in bestBBox.keys():
                print("No bbox found for " + field)
                bestBBox[field] = fieldpos[field]
            
        #manual fix for co2.rr being misread because it includes co2.fi
        if bestBBox['co2.rr'][0] < center_coords['co2.fi'][0] < bestBBox['co2.rr'][2] and bestBBox['co2.rr'][1] < center_coords['co2.fi'][1] < bestBBox['co2.rr'][3]:
                xmin = bestBBox['co2.rr'][0]
                ymin = bestBBox['co2.rr'][1]
                xmax = bestBBox['co2.rr'][2]
                ymax = bestBBox['co2.rr'][3] 
                bestBBox['co2.rr'] = (int(xmin + (xmax - xmin)/2) , ymin, xmax, ymax)
                bestBBox['co2.fi'] = (xmin, ymin, int((xmin + (xmax - xmin)/2)), ymax)

        for field, bbox in bestBBox.items():
            imageDict[field] = image.crop(bbox)
    return imageDict

def get_parameter_imgs(image, monitor, bbox_adjustment):

    ideal_height = 100

    for filename in os.listdir("processed_images"):
        os.remove(os.path.join("processed_images", filename))

    image.save(os.path.join("processed_images", "Img.png"))

    origSize = image.size
    imageDict = get_field_cropped_imgs(image, monitor, bbox_adjustment)

    for key in imageDict.keys():

        img = imageDict[key]
        img = resize_height(img, ideal_height)

        # black_image = Image.new('RGB', origSize, (0, 0, 0))
        # black_image.paste(img, [int(origSize[0]/2), int(origSize[1]/2)])
        # img = black_image

        img = pil_to_opencv(img)
        
        # img = scikit_denoising(img)
        # img = bilateral_filter_noseremover(img)
        # img = remove_noise(img)
        # img = gaussianBlur(img)
        # img = remove_noise(img)

        # factor = 3 + 
        img = enhanceContrast(img, 4)

        # img = despeckle_image(img, 5, 1)
        img = enhanceSharpness(img, 2)
        # img = colorThresholding(img)
        img = get_grayscale(img)

        # img = guassianBlur(img)
        # img = equalizeHist(img)
        # img = thresholding(img)
        # img = size_threshold(img, 4000, 99999999999)
        img = flipGreyscale(img)
        # img = normalise(img)

        # Save the images
        img = cv2_to_pil(img)
        imageDict[key] = img
        imageDict[key].save(os.path.join("processed_images", key + "-img.png"))

    return imageDict


def process_img(imgName):
    image = Image.open(imgName)

    # Get image in the right orientation
    modified_image = image.transpose(Image.FLIP_TOP_BOTTOM)
    modified_image = modified_image.transpose(Image.FLIP_LEFT_RIGHT)

    # Gets processed images for each field which should be present
    imgs = get_parameter_imgs(modified_image)
    return imgs


# TO TRY:
# - keystone correction
# - image despeckling
# - better AI
