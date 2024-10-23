import os
from PIL import Image, ImageDraw, ImageFont
import easyocr
import numpy as np

from monitor_values import HospitalMonitor, OldMonitor

def draw_boxes(image, box, text):
    """Draws a red box with some text in the corner on a given image, and returns the image with the box drawn in it

    Args:
        image: PIL image to draw on
        box: bounding box, a tuple of 4 values (xmin, ymin, xmax, ymax)
        text: the text to draw on the image

    Returns:
        _type_: _description_
    """
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    draw.text((box[0], box[1]), text, fill="red", font=font)
    draw.rectangle(box, outline="red")
    return image

def show_bboxes(center_coords):
    """Iterates through every image in the images directory, and uses EasyOCR to generate bounding boxes for where EasyOCR detects text,
    and draws those bounding boxes on the image. This allows generation of EasyOCR bounding boxes on every image in images directory.
    It also draws the centre coordinates of fields that are specified in the Monitor, so you can see where easyOCR's text estimates are accurate or not.

    Args:
        center_coords (_type_): The monitor layout's centre coordinates for its field bounding boxes
    """
    for q in range(1, 182):
        print(q)
        img = Image.open("images/" + str(q) + "tmp.jpg")
        img = img.transpose(Image.FLIP_TOP_BOTTOM)
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
        result = reader.readtext(np.array(img)) 
        new_img = img
        for res in result:
            x_values = [point[0] for point in res[0]]
            y_values = [point[1] for point in res[0]]
            xmin = min(x_values)
            ymin = min(y_values)
            xmax = max(x_values)
            ymax = max(y_values)
            new_img = draw_boxes(new_img, (xmin, ymin, xmax, ymax), res[1])
        
        #show the centre coords as well
        for key in center_coords.keys():
            field_x = center_coords[key][0]
            field_y = center_coords[key][1]
            new_img = draw_boxes(new_img, (field_x, field_y, field_x+2, field_y+2), '') 

        new_img.save("bboxImgs/new_image" + str(q) + ".png")

def show_center_coords(center_coords, field_coords):
    """Draws bounding boxes for fields as well as the centers of those field bounding boxes onto an image

    Args:
        center_coords (_type_): Center coordinates of the field bounding boxes
        field_coords (_type_): Field bounding boxes
    """
    img = Image.open(os.path.join("misc_images", "image.png"))
    img = img.transpose(Image.FLIP_TOP_BOTTOM)
    img = img.transpose(Image.FLIP_LEFT_RIGHT)
    extracted_data = []
    for key in center_coords.keys():
        field_x = center_coords[key][0]
        field_y = center_coords[key][1]
        img = draw_boxes(img, (field_x, field_y, field_x+2, field_y+2), key)
        img = draw_boxes(img, field_coords[key], '')
    img.save("field_centers.png")

def show_hospital_monitor_bboxes():
    """Draws bounding boxes on the hospital monitor images 33tmp.jpg based off of the coordinates specified in the HospitalMonitor.
    It then saves the image as field_centers.jpg
    This function is used for testing the field coordinates specified in HospitalMonitor
    """
    field_coords = HospitalMonitor().get_field_pos()
    img = Image.open(os.path.join("images", "normalhospital_images", "33tmp.jpg"))
    img = img.transpose(Image.FLIP_TOP_BOTTOM)
    img = img.transpose(Image.FLIP_LEFT_RIGHT)
    extracted_data = []
    for key in field_coords.keys():
        img = draw_boxes(img, field_coords[key], key)
    img.save("field_centers.png")
    

if __name__ == "__main__":
    global reader
    print("loading EasyOCR")
    reader = easyocr.Reader(['en']) # this needs to run only once to load the model into memory

    # center_coords = OldMonitor.get_pos_centres()
    # field_coords = OldMonitor.get_field_pos()
    # show_center_coords(center_coords, field_coords)
    # show_bboxes(center_coords)
    show_hospital_monitor_bboxes()