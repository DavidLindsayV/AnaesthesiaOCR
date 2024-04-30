import os
from process_img import process_img
from query import extract_data
from write_to_csv import write_to_csv
from datetime import datetime


def checkAnswers(extracted_data):
    ###Tests the answers to see if the numbers extracted match image.png
    print()
    expected_data = {'ecg.hr': '76', 'co2.et': '37', 'co2.fi': '0', 'co2.rr': '16', 'p1.sys': '139', 'p1.dia': '79', 'p1.mean': '(94)', 'aa.et': '0.80', 'aa.fi': '2.1'}
    print(expected_data)
    print(extracted_data)

    for key in expected_data.keys():
        if expected_data[key] != extracted_data[key]:
            print("WRONG " + key + " Expected: " + expected_data[key] + " Actual: " + extracted_data[key])

def test_with_one_image():
    imagesDict = process_img("image.png")
    time = datetime.now()
    extracted_data = [extract_data(imagesDict)]
    print("Time taken to perform AI OCR = " + str(datetime.now() - time))
    checkAnswers(extracted_data[0])
    write_to_csv(extracted_data)

def write_to_csv_all_images():
    starttime = datetime.now()
    ocr_data = []
    num_images = len(os.listdir("images"))
    count = 1
    for filename in os.listdir("images"):
        print("Processing image " + str(count) + "/" + str(num_images))
        count += 1
        imagesDict = process_img(os.path.join("images", filename))
        ocr_data.append(extract_data(imagesDict))
    write_to_csv(ocr_data)
    print("Completed! Time taken = " + str(datetime.now() - starttime))

test_with_one_image()