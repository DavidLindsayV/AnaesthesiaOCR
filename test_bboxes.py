from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageFont
import easyocr
import numpy as np

from monitor_values import OldMonitor

def draw_boxes(image, box, text):
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    draw.text((box[0], box[1]), text, fill="red", font=font)
    draw.rectangle(box, outline="red")
    return image

def show_bboxes(center_coords):
    for q in range(1, 182):
        print(q)
        img = Image.open("images/" + str(q) + "tmp.jpg")
        img = img.transpose(Image.FLIP_TOP_BOTTOM)
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
        result = reader.readtext(np.array(img)) #this removes bounding box and confidence info
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
    img = Image.open("image.png")
    img = img.transpose(Image.FLIP_TOP_BOTTOM)
    img = img.transpose(Image.FLIP_LEFT_RIGHT)
    extracted_data = []
    for key in center_coords.keys():
        field_x = center_coords[key][0]
        field_y = center_coords[key][1]
        img = draw_boxes(img, (field_x, field_y, field_x+2, field_y+2), key)
        img = draw_boxes(img, field_coords[key], '')
    img.save("field_centers.png")

    

global reader
print("loading EasyOCR")
reader = easyocr.Reader(['en']) # this needs to run only once to load the model into memory

center_coords = OldMonitor.pos_centres
field_coords = OldMonitor.field_pos
# show_center_coords(center_coords, field_coords)
show_bboxes(center_coords)