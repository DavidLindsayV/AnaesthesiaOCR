###Where querying the AI occurs###

from io import BytesIO
import json
import numpy
import requests
import os
import base64
from PIL import Image
import cv2

from process_img import process_img

# model_id = "dd80ac37-ed9e-405c-87c9-a3285785677a" #This model is a 0-training model


#Pixel coordinates of each Physiological parameter:
#Heart rate x:500-580 y:160-230


api_key = os.getenv("NANONETS_API_KEY")

url = "https://app.nanonets.com/api/v2/OCR/FullText"

imagesDict = process_img("image.png")

files = []
for key in imagesDict.keys():
    files.append( ('file', (key, open(os.path.join("processed_images", key + "-img.png"), 'rb'), 'application/pdf')) )

# files=[
#  ('file',('ecto2-img',open('processed_images/ecto2-img.png','rb'),'application/pdf')), 
#   ('file',('heartrate-img',open('processed_images/heartrate-img.png','rb'),'application/pdf'))
# ]

headers = {}


response = requests.request("POST", url, headers=headers, files=files, auth=requests.auth.HTTPBasicAuth(api_key, ''))
response = response.json()
# print(response)

for result in response['results']:
    print(result['filename'] + " " + result['page_data'][0]['words'][0]['text'].strip())


# print(response['results'][0]['page_data'][0]['raw_text'].strip()) #this expression extracts the raw text from an entire image, all texts together
# print(response['results'][0]['page_data'][0]['words'][0]['text'].strip()) #this expression extracts the first bit of text found. However, unreliable if no text is found

