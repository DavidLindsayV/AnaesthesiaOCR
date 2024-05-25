import tempfile
from PIL import Image, ImageEnhance, ImageFilter

import os

import cv2
import numpy as np
from PIL import Image
from deskew import determine_skew
from typing import Tuple, Union
import math

from monitor_values import OldMonitor
from query import find_bboxes


def normalise(img):
    norm_img = np.zeros((img.shape[0], img.shape[1]))
    img = cv2.normalize(img, norm_img, 0, 255, cv2.NORM_MINMAX)
    return img


def remove_noise(image):
    # return cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 15)
    return cv2.fastNlMeansDenoisingColored(image)


def thresholding(image):
    # min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(image)
    # image = cv2.threshold(image, thresh, 255, cv2.THRESH_BINARY)[1]
    # image = cv2.threshold(image, min_val + (max_val-min_val)*percent, 255, cv2.THRESH_BINARY)[1]
    # return image
    # return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    image = cv2.medianBlur(image,5)
    return cv2.adaptiveThreshold(image,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,2)


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

def get_field_cropped_imgs(image):
    fieldCroppingMode = "BBox_Detection_Old_Monitor"

    oldMonitor_Fieldpos = OldMonitor.field_pos
    imageDict = {}

    if fieldCroppingMode == "Manual_Old_Monitor":
        for key, box in oldMonitor_Fieldpos.items():
            imageDict[key] = image.crop(box)

    elif fieldCroppingMode == "BBox_Detection_Old_Monitor":
        center_coords = {}
        for key, box in oldMonitor_Fieldpos.items():
            center_coords[key] = ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2)

        bboxes = find_bboxes(image)

        bestBBox = {}
        for field, coords in center_coords.items():
            for bbox in bboxes:
                xmin = bbox.box[0]
                ymin = bbox.box[1]
                xmax = bbox.box[2]
                ymax = bbox.box[3]
                if xmin <= coords[0] <= xmax and ymin <= coords[1] <= ymax:
                    if not field in bestBBox.keys():
                        bestBBox[field] = bbox.box
                    else:
                        # If the new bbox found is smaller than the previous one found
                        if (xmax - xmin) * (ymax - ymin) < (
                            bestBBox[field][2] - bestBBox[field][0]
                        ) * (bestBBox[field][3] - bestBBox[field][1]):
                            bestBBox[field] = bbox.box

        for field in oldMonitor_Fieldpos.keys():
            if not field in bestBBox.keys():
                print("No bbox found for " + field)
                bestBBox[field] = oldMonitor_Fieldpos[field]
            
        for field, bbox in bestBBox.items():
            imageDict[field] = image.crop(bbox)
    return imageDict

def get_parameter_imgs(image):

    ideal_height = 100

    for filename in os.listdir("processed_images"):
        os.remove(os.path.join("processed_images", filename))

    image.save(os.path.join("processed_images", "Img.png"))

    origSize = image.size
    imageDict = get_field_cropped_imgs(image)

    for key in imageDict.keys():

        img = imageDict[key]
        img = resize_height(img, ideal_height)

        # black_image = Image.new('RGB', origSize, (0, 0, 0))
        # black_image.paste(img, [int(origSize[0]/2), int(origSize[1]/2)])
        # img = black_image

        img = pil_to_opencv(img)
        img = set_image_dpi(img)
        img = remove_noise(img)


        # factor = 3 + 
        img = enhanceContrast(img, 8)

        # img = despeckle_image(img, 5, 1)
        # img = enhanceSharpness(img, 2)
        # img = colorThresholding(img)
        img = get_grayscale(img)

        # img = guassianBlur(img)
        # img = equalizeHist(img)
        # img = thresholding(img)
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
