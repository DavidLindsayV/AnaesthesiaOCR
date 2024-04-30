###Where querying the AI occurs###

import os
from nanonets import NANONETSOCR
import pytesseract
import requests

def extract_data(imagesDict):
    model = "Nanonets_Requests"

    filenames = {}
    files = []
    for key in imagesDict.keys():
        filenames[key] = os.path.join("processed_images", key + "-img.png")
        files.append( ('file', (key, open(filenames[key]), 'application/pdf')))
        # files.append( ('file', (key, open(os.path.join("processed_images", key + "-img.png"), 'rb'), 'application/pdf')) )

    extracted_data = {}

    if model == "Nanonets_pythonOCR":
        model = NANONETSOCR()
        # api_key = os.getenv("NANONETS_API_KEY")
        #TODO remove this reference to api key and delete this key
        api_key="7360ff90-e64a-11ee-a0dd-1eb7c1521e8e"

        model.set_token(api_key)

        for key, value in filenames.items():
            pred_json = model.convert_to_prediction(value)
            # print(key + " " + pred_json['results'][0]['page_data'][0]['words'][0]['text'].strip())
            extracted_data[key] = pred_json['results'][0]['page_data'][0]['words'][0]['text'].strip()

    elif model == "Nanonets_Requests":
        reqFiles = []
        for key in imagesDict.keys():
            reqFiles.append( ('file', (key, open(os.path.join("processed_images", key + "-img.png"), 'rb'), 'application/pdf')) )
        # reqFiles.append(('file', (key, open("image.png", 'rb'), 'application/pdf')))

        headers = {}
        # api_key = os.getenv("NANONETS_API_KEY")
        #TODO remove this reference to api key and delete this key
        api_key="7360ff90-e64a-11ee-a0dd-1eb7c1521e8e"

        url = "https://app.nanonets.com/api/v2/OCR/FullText"

        response = requests.request("POST", url, headers=headers, files=reqFiles, auth=requests.auth.HTTPBasicAuth(api_key, ''))
        response = response.json()
        # print(response)
        for result in response['results']:
            first_text = ''
            if len(result['page_data'][0]['words']) != 0:
                first_text = result['page_data'][0]['words'][0]['text'].strip()
            # print(result['filename'] + " first_text=" + first_text + " full_text=" + result['page_data'][0]['raw_text'].strip())
            extracted_data[result['filename']] = first_text
        # print(response['results'][0]['page_data'][0]['raw_text'].strip()) #this expression extracts the raw text from an entire image, all texts together
        # print(response['results'][0]['page_data'][0]['words'][0]['text'].strip()) #this expression extracts the first bit of text found. However, unreliable if no text is found


    elif model == "PyTesseract":

        for key, value in filenames.items():
            text = pytesseract.image_to_string(value,lang='eng')
            # print(key + " value=" + text)
            extracted_data[key] = text

    elif model == "EasyOCR":
        import easyocr
        reader = easyocr.Reader(['en']) # this needs to run only once to load the model into memory
        for key in imagesDict.keys():
            result = reader.readtext(os.path.join("processed_images", key + "-img.png"), detail=0) #this removes bounding box and confidence info
            extracted_data[key] = result[0]
            print(result)

    return extracted_data
