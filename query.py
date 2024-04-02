###Where querying the AI occurs###

import os
from nanonets import NANONETSOCR
import json

import pytesseract
import requests

from process_img import process_img



model = "Nanonets_Requests"

imagesDict = process_img("image.png")

filenames = {}
files = []
for key in imagesDict.keys():
    filenames[key] = os.path.join("processed_images", key + "-img.png")
    files.append( ('file', (key, open(filenames[key]), 'application/pdf')))
    # files.append( ('file', (key, open(os.path.join("processed_images", key + "-img.png"), 'rb'), 'application/pdf')) )


if model == "Nanonets_pythonOCR":
    model = NANONETSOCR()
    api_key = os.getenv("NANONETS_API_KEY")
    model.set_token(api_key)

    for key, value in filenames.items():
        pred_json = model.convert_to_prediction(value)
        print(key + " " + pred_json['results'][0]['page_data'][0]['words'][0]['text'].strip())        

elif model == "Nanonets_Requests":
    reqFiles = []
    for key in imagesDict.keys():
        reqFiles.append( ('file', (key, open(os.path.join("processed_images", key + "-img.png"), 'rb'), 'application/pdf')) )

    headers = {}
    api_key = os.getenv("NANONETS_API_KEY")
    url = "https://app.nanonets.com/api/v2/OCR/FullText"

    response = requests.request("POST", url, headers=headers, files=reqFiles, auth=requests.auth.HTTPBasicAuth(api_key, ''))
    response = response.json()

    for result in response['results']:
        print(result['filename'] + " " + result['page_data'][0]['words'][0]['text'].strip())

    # print(response['results'][0]['page_data'][0]['raw_text'].strip()) #this expression extracts the raw text from an entire image, all texts together
    # print(response['results'][0]['page_data'][0]['words'][0]['text'].strip()) #this expression extracts the first bit of text found. However, unreliable if no text is found

elif model == "PyTesseract":

    print(filenames)
    for key, value in filenames.items():
        text = pytesseract.image_to_string(value,lang='eng')
        print(key + " " + text)