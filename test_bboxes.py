from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageFont
import easyocr
import numpy as np

def draw_boxes(image, box, text):
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    draw.text((box[0], box[1]), text, fill="red", font=font)
    draw.rectangle(box, outline="red")
    return image

global reader
print("loading EasyOCR")
reader = easyocr.Reader(['en']) # this needs to run only once to load the model into memory

for q in range(1, 182):
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
    new_img.save("bboxImgs/new_image" + str(q) + ".jpg")

    # center_coords = {'ecg.hr': [540, 195], 'co2.et': [487, 347.5], 'co2.f1': [475, 377], 'co2.rr': [507, 375], 'p1.sys': [445, 415], 'p1.dia': [505, 415], 'p1.mean': [441, 440], 'aa.et': [137, 412], 'aa.fi': [140, 432]}

    # extracted_data = []
    # for key in center_coords.keys():
    #     field_x = center_coords[key][0]
    #     field_y = center_coords[key][1]
    #     for res in result:
    #         x_values = [point[0] for point in res[0]]
    #         y_values = [point[1] for point in res[0]]
    #         xmin = min(x_values)
    #         ymin = min(y_values)
    #         xmax = max(x_values)
    #         ymax = max(y_values)
    #         if xmin <= field_x <= xmax and ymin <= field_y <= ymax:
    #             extracted_data[key] = res[1]

    # print(result)
