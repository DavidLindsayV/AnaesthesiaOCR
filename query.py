###Where querying the AI occurs###

import io
import os
import re
from nanonets import NANONETSOCR
import numpy as np
import pytesseract
import requests
import easyocr
from PIL import Image

from monitor_values import Field_Ranges

reader = None


# TODO: sometimes p1.sys and p1.dia have no value displayed. The current sanitycheck will convert this to --- instead of leaving blank
# TODO: check the length of strings. p1.sys should have max 3 chars, p1.mean is 2 or 3 digits

def removeNonNumberChar(input):
    """Removes non numerical characters from the input

    Args:
        input (str): input string

    Returns:
        str: input string with nonnumerical characters removed
    """
    return re.sub(r"\D", "", input)


def inRange(field, num):
    """Checks if a string num is within the range of it's field

    Args:
        field (str): hl7 code of a physiological parameter
        num (str): a string of a number of that physiological parameter

    Returns:
        bool: whether the number is within the expected range of that physiological parameter
    """
    return (
        Field_Ranges.field_ranges[field][1]
        <= float(num)
        <= Field_Ranges.field_ranges[field][0]
    )


def make_in_range(field, num):
    """A function which takes a string which is out of the expected numerical range, and tries to make it fit in the expected numerical range by removing one character from the front or back

    Args:
        field: the field hl7 code
        num: the string of a number that is being improved to fit inside the expected range

    Returns:
        str: The improved num
    """

    try:  # check that num can be read as a number
        float(num)
    except ValueError:
        return num

    if inRange(field, num):
        return num
    else:
        if len(num) <= 1:  # if the num is 1 character, you can't make substrings of it
            return num

        if float(num) > Field_Ranges.field_ranges[field][0]:  # If you are above the max
            preNum = num[:-1]
            postNum = num[1:]
            # print(preNum)
            # print(postNum)
            # If removing the first or last character makes the number in the correct range, and  you can clearly tell which to remove
            if inRange(field, preNum) and not inRange(field, postNum):
                return preNum
            if inRange(field, postNum) and not inRange(field, preNum):
                return postNum
            # If it begins or ends with '1' (a common misread of ')' or '/')
            if num.endswith("1") and inRange(field, preNum):
                return preNum
            if num.startswith("1") and inRange(field, postNum):
                return postNum
            if inRange(field, preNum) and inRange(
                field, postNum
            ):  # if both are valid, choose the one which removes the first character TODO this is arbitrary
                return postNum
        # Give up, you can't make this number fit the range
        print("Failed to make into correct range: " + field + " " + num) #TODO this should return the null value if you can't fit in the correct range
        return num


def sanitycheck_data(extracted_data):
    """Takes in data that was etracted via OCR and postprocesses it to make it more accurate
    Performs fixes such as removing non-numerical characters or trying to fix numbers to make them in an appropriate range

    Args:
        extracted_data (dict): the data that was extracted via OCR 

    Returns:
        dict: The extracted data dict, but with the extracted text improved to be less erroneous
    """
    
    print("Data pre-sanity check:") #TODO make the sanity checking depend on monitor
    print(extracted_data)

    for key in extracted_data.keys():
        extracted_data[key] = extracted_data[key].replace("O", "0")
        extracted_data[key] = extracted_data[key].replace("B", "8")
        if not any(
            char.isdigit() for char in extracted_data[key]
        ):  # If the string is horribly wrong, or is empty, or is ---
            extracted_data[key] = (
                "---"  # easyOCR often reads --- as empty string. This fixes that problem TODO fix this to work with oldmonitor and new. Make the none character depend on the monitor.
            )
            continue

        if key == "p1.mean":
            extracted_data[key] = (
                "(" + make_in_range(key, removeNonNumberChar(extracted_data[key])) + ")"
            )
        elif key == "p1.sys":
            if "/" in extracted_data[key]:
                extracted_data[key] = extracted_data[key].split("/")[0]
            extracted_data[key] = removeNonNumberChar(extracted_data[key])
            extracted_data[key] = make_in_range(key, extracted_data[key])
        elif key == "p1.dia":
            if "/" in extracted_data[key]:
                extracted_data[key] = extracted_data[key].split("/")[1]
            extracted_data[key] = removeNonNumberChar(extracted_data[key])
            extracted_data[key] = make_in_range(key, extracted_data[key])
        elif key == "co2.rr":
            if " " in extracted_data[key]:
                extracted_data[key] = extracted_data[key].split(" ")[1]
            extracted_data[key] = removeNonNumberChar(extracted_data[key])
            extracted_data[key] = make_in_range(key, extracted_data[key])
        elif key == "co2.fi":
            if " " in extracted_data[key]:
                extracted_data[key] = extracted_data[key].split(" ")[0]
            extracted_data[key] = removeNonNumberChar(extracted_data[key])
            extracted_data[key] = make_in_range(key, extracted_data[key])
        elif key == "aa.et" or key == "aa.fi":
            extracted_data[key] = re.sub(r"[^\d.]", "", extracted_data[key])
            if not "." in extracted_data[key] and len(extracted_data[key]) > 1:
                extracted_data[key] = (
                    extracted_data[key][0] + "." + extracted_data[key][1:]
                )
            elif not "." in extracted_data[key] and len(extracted_data[key]) == 1:
                extracted_data[key] = extracted_data[key][0] + ".0"
            extracted_data[key] = make_in_range(key, extracted_data[key])
        else:
            # key == "ecg.hr" or key == "co2.et" or key == "spo2.pr" or key == "spo2.SpO2":
            extracted_data[key] = removeNonNumberChar(
                extracted_data[key]
            )  # remove any non-number characters
            extracted_data[key] = make_in_range(key, extracted_data[key])

    return extracted_data


class BBox:
    """A class to represent a bounding box
    """

    def __init__(self, box, text):
        self.box = box  # xmin ymin xmax ymax
        self.text = text

    def __repr__(self):
        return f"BBox(array={self.box}, string='{self.text}')"


def find_bboxes(image):
    """Uses EasyOCR to find bounding boxes of all text within the given image

    Args:
        image: image to find bounding boxes of text in

    Returns:
        list: a list of BBox objects
    """
    model = "EasyOCR"
    bboxes = []

    if model == "EasyOCR":
        global reader
        if reader == None:
            print("loading EasyOCR")
            reader = easyocr.Reader(
                ["en"]
            )  # this needs to run only once to load the model into memory
        result = reader.readtext(np.array(image))
        for res in result:
            x_values = [point[0] for point in res[0]]
            y_values = [point[1] for point in res[0]]
            xmin = min(x_values)
            ymin = min(y_values)
            xmax = max(x_values)
            ymax = max(y_values)
            bboxes.append(BBox((xmin, ymin, xmax, ymax), res[1]))
    return bboxes


def extract_data(imagesDict):
    """Extracts one text field for each image in imagesDict, postprocesses it, and returns it as a dict of physiological parameter code to extracted text

    Args:
        imagesDict (_type_): The dict of images that need data extracted via OCR

    Returns:
        dict: The dict of physiological parameter codes and what text has been extracted for each field
    """
    
    model = "EasyOCR" #specifies which model is used

    filenames = {}
    # files = []
    for key in imagesDict.keys():
        filenames[key] = os.path.join("processed_images", key + "-img.png")
        # files.append( ('file', (key, open(filenames[key]), 'application/pdf')))
        # files.append( ('file', (key, open(os.path.join("processed_images", key + "-img.png"), 'rb'), 'application/pdf')) )

    extracted_data = {}

    if model == "Nanonets_pythonOCR":
        model = NANONETSOCR()
        # api_key = os.getenv("NANONETS_API_KEY")
        api_key = "7360ff90-e64a-11ee-a0dd-1eb7c1521e8e"

        model.set_token(api_key)

        for key, value in filenames.items():
            pred_json = model.convert_to_prediction(value)
            # print(key + " " + pred_json['results'][0]['page_data'][0]['words'][0]['text'].strip())
            extracted_data[key] = pred_json["results"][0]["page_data"][0]["words"][0][
                "text"
            ].strip()

    elif model == "Nanonets_Requests":
        reqFiles = []
        for key in imagesDict.keys():
            pil_image = imagesDict[key]
            bytes_io = io.BytesIO()
            pil_image.save(bytes_io, format="PNG")
            bytes_io.seek(0)
            buffered_reader = io.BufferedReader(bytes_io)
            reqFiles.append(("file", (key, buffered_reader, "application/pdf")))
        # reqFiles.append(('file', (key, open("image.png", 'rb'), 'application/pdf')))

        headers = {}
        # api_key = os.getenv("NANONETS_API_KEY")
        api_key = "7360ff90-e64a-11ee-a0dd-1eb7c1521e8e"

        url = "https://app.nanonets.com/api/v2/OCR/FullText"

        response = requests.request(
            "POST",
            url,
            headers=headers,
            files=reqFiles,
            auth=requests.auth.HTTPBasicAuth(api_key, ""),
        )
        response = response.json()
        for result in response["results"]:
            first_text = ""
            if len(result["page_data"][0]["words"]) != 0:
                first_text = result["page_data"][0]["words"][0]["text"].strip()
            # print(result['filename'] + " first_text=" + first_text + " full_text=" + result['page_data'][0]['raw_text'].strip())
            extracted_data[result["filename"]] = first_text
        # print(response['results'][0]['page_data'][0]['raw_text'].strip()) #this expression extracts the raw text from an entire image, all texts together
        # print(response['results'][0]['page_data'][0]['words'][0]['text'].strip()) #this expression extracts the first bit of text found. However, unreliable if no text is found

    elif model == "PyTesseract":

        for key, value in filenames.items():
            text = pytesseract.image_to_string(value, lang="eng")
            extracted_data[key] = text

    elif model == "EasyOCR":
        global reader
        if reader == None:
            print("loading EasyOCR")
            reader = easyocr.Reader(
                ["en"]
            )  # this needs to run only once to load the model into memory
        detail = 1
        for key in imagesDict.keys():
            result = reader.readtext(
                np.array(imagesDict[key]), detail=detail
            )  # detail = 0 removes bounding box and confidence info
            if len(result) > 0:
                if detail == 0:
                    extracted_data[key] = result[0]
                else:
                    extracted_data[key] = result[0][1]
            else:
                extracted_data[key] = ""

    extracted_data = sanitycheck_data(extracted_data)
    return extracted_data


# img = Image.open("processed_images\co2.rr-img.png")
# print(extract_data({'co2.rr': img }))
# print(make_in_range('p1.mean', removeNonNumberChar("676")))
