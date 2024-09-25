import os
import random
from check_accuracy import get_expected_data_row
from monitor_values import CustomMonitor, HospitalMonitor, OldMonitor
from process_img import process_img
from query import extract_data
from write_to_csv import is_number, parse_number, write_to_csv
from datetime import datetime
import sys

def checkAnswersForImg(imgNum, ocrAnswers, expected_data):
    print("Image = " + str(imgNum) + "tmp.jpg")
    print(expected_data)
    print(ocrAnswers)
    for key in ocrAnswers.keys():
        if expected_data[key] != ocrAnswers[key]:
            print("WRONG " + key + " Expected: " + expected_data[key] + " Actual: " + ocrAnswers[key])

def get_sheet_name_from_folder_path(imgPath):
    if "brightreflectionhospital" in imgPath:
        return "BrightReflectionHospital"
    elif "darkhospital_images" in imgPath:
        return "DarkHospital"
    elif "normalhospital_images" in imgPath:
        return "NormalHospital"
    elif "oldmonitor_images" in imgPath:
        return "OldMonitor"
    elif "repositionedcamerahospital_images" in imgPath:
        return "RepositionedCameraHospital"

def test_with_img(imgPath, monitor): 
    if monitor == "HospitalMonitor":
        monitor = HospitalMonitor()
    elif monitor == "OldMonitor":
        monitor = OldMonitor()
    elif monitor == "CustomMonitor":
        monitorfile = input("Please enter the path to the file to load a custom monitor from: ")
        monitor = CustomMonitor(monitorfile)
    else:
        print("invalid monitor name entered")
        return
    
    bbox_adjustment = True

    #Get extracted data
    imagesDict = process_img(imgPath, monitor, bbox_adjustment)
    time = datetime.now()
    extracted_data = [extract_data(imagesDict)]
    print("Time taken to perform AI OCR = " + str(datetime.now() - time))

    #Get expected data
    imgNum = imgPath.split(os.path.sep)[-1].replace("tmp.jpg", "")
    sheet_name = get_sheet_name_from_folder_path(imgPath)
    expected_data = get_expected_data_row(sheet_name, list(extracted_data[0].keys()), imgNum)
    checkAnswersForImg(imgNum, extracted_data[0], expected_data)

def test_with_random_image(imgFolder):
    path = os.path.join("images", imgFolder)
    num_images = len(os.listdir(dir))
    imgNum = random.randint(1, num_images)
    test_with_img(os.path.join(path, imgNum + "tmp.jpg"))

def write_to_csv_all_images(img_folder, monitor):
    dir = os.path.join("images", img_folder)

    if monitor == "HospitalMonitor":
        monitor = HospitalMonitor()
    elif monitor == "OldMonitor":
        monitor = OldMonitor()
    elif monitor == "CustomMonitor":
        monitorfile = input("Please enter the path to the file to load a custom monitor from: ")
        monitor = CustomMonitor(monitorfile)
    else:
        print("invalid monitor name entered")
        return

    bbox_adjustment = True

    starttime = datetime.now()
    ocr_data = []
    count = 1
    num_images = len(os.listdir(dir))
    maxImageTime = starttime - starttime
    for i in range(1, num_images + 1):
        imagestarttime = datetime.now()
        print("Processing image " + str(count) + "/" + str(num_images))
        count += 1
        filename = os.path.join(dir, str(i) + "tmp.jpg")
        imagesDict = process_img(filename, monitor, bbox_adjustment)
        imageFinishedTime = datetime.now()
        if (imageFinishedTime - imagestarttime) > maxImageTime:
            maxImageTime = (imageFinishedTime - imagestarttime)
        print(filename + " Time taken: " + str(imageFinishedTime - imagestarttime))
        ocr_data.append(extract_data(imagesDict))
    write_to_csv(ocr_data)
    print("Completed! Time taken = " + str(datetime.now() - starttime))
    print("Longest time to process an image: " + str(maxImageTime))

def get_latest_received_img_data(monitor):  
    bbox_adjustment = True
    starttime = datetime.now()
    os.chdir('C:\\Users\\david\\Documents\\University_courses\\University_2024_Tri1\\ENGR489\\engr489-anaesthesiaocr')
    num_images = len(os.listdir("images_from_rpi"))
    imageName = str(num_images) + "tmp.jpg"
    print("Processing image " + imageName)
    filename = os.path.join("images_from_rpi", imageName)
    imagesDict = process_img(filename, monitor, bbox_adjustment)
    data = extract_data(imagesDict)
    toDelete = []
    for field in data.keys():
        if is_number(data[field]):
            number = parse_number(data[field])
            data[field] = number
        else:
            toDelete.append(field)
    #Delete all fields that cannot be parsed into numbers
    for field in toDelete:
        del data[field]
    data['rtime'] = starttime
    print(imageName + "OCR Completed! Time taken = " + str(datetime.now() - starttime))
    return data

if __name__ == "__main__":
    # if len(sys.argv) > 1:
    #     test_with_img(sys.argv[1])
    # else:
    #     print("Need to know the path to the image to test")

    # if len(sys.argv) == 2:
    #     test_with_random_image(sys.argv[1]) 
    # else:
    #     print("Need to know what folder of images to choose randomly from. Choose one of the subfolder names within images folder")

    if len(sys.argv) == 3:
        write_to_csv_all_images(sys.argv[1], sys.argv[2])
    else:
        print("Please provide 2 cmd arguments. First, one of the names of the image subfolders within the image folder. Secondly, which monitor to use")
        print("The monitor options are: OldMonitor, HospitalMonitor, CustomMonitor")