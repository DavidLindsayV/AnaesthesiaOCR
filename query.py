###Where querying the AI occurs###

import requests
import os
import base64
from PIL import Image

# model_id = "dd80ac37-ed9e-405c-87c9-a3285785677a" #This model is a 0-training model





api_key = os.getenv("NANONETS_API_KEY")

url = "https://app.nanonets.com/api/v2/OCR/FullText"

image = Image.open("image.png")
modified_image = image.transpose(Image.FLIP_TOP_BOTTOM)
modified_image = modified_image.transpose(Image.FLIP_LEFT_RIGHT)
modified_image.save("mod-img.png")

files=[
  ('file',('mod-img.png',open('mod-img.png','rb'),'application/pdf'))
]
headers = {}

response = requests.request("POST", url, headers=headers, files=files, auth=requests.auth.HTTPBasicAuth(api_key, ''))

print(response.text)