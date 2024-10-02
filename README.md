# OCR for anaesthesia monitors

Optical Character Recognition for data acquisition from anaesthesia monitors (Industry Project)

Description
The purpose of this project is to develop an Optical Character Recognition Unit that can read data from anaesthesia monitor screens. A basic prototype that consists of a Raspberry Pi and Raspberry Pi Camera has been developed. This unit attaches to anaesthesia monitors and has been shown to be able to recognize the data displayed on an anaesthesia monitor display. Accuracy is however still wanting and various enhancements are desired.


Detail
This is a continuation of the 2022 ENGR301/302 project that developed the basic prototype unit. There are TWO aspects of the current system that are outstanding and would be the immediate desired outcomes of this project:

1. Enhancing the accuracy of the character recognition.

2. Identifying the two parameters that could be confused (Heart rate between 90 and 100bpm. and oxygen saturation that could be between 90 and 100%), maybe by identifying the parameter by the colour, or maybe by following the trend of previous values. e.g. previous values of >100 would make the parameter heart rate.

3. Achieve the above from multiple point of views, that is, the camera being placed in different angles/elevations in front of the monitor.

Student Capabilities
Knowledge of AI/ML for optical character recognition.

Suitable programming language for implementing AI/ML algorithms to improve the accuracy of the OCR.

Major this project is best suited for
SWEN

## Repository contents explanation

images: 
The folder that contains images obtained by attaching the rpi mount to hospital monitors. 
The folder has 5 subfolders:
- brightreflectionhospital_images: images taken 21/05/2024 of a monitor with bright reflections on the screen
- darkhospital_images: images taken 21/05/2024 of a monitor in a darkened room
- normalhospital_images: images taken 21/05/2024 of a monitor under normal conditions
- oldmonitor_images: images taken in 2022 of a datex-ohmeda monitor under normal conditions
- repositionedcamerahospital_images: images taken 21/05/2024 when the camera mount was readjusted slightly to get a shift in perspective
monitor_data.xslx: a excel file containing all the values displayed in each image in an excel sheet. 

images_from_rpi: 
A folder for the rpi to send newly captured images into

misc_images: miscellaneous images

processed_images: images that are created of each physiological parameter after it is extracted from the overall image and preprocessed to be more readable

Hardware: a folder containing files related to the hardware (the rpi) and how to use it
Hardware_Use_Instructions.md are instructions on how to use the rpi
The subfolder Code_For_Image_Capture(32_bit) is the code that is run on the rpi to perform image capture and ssh sending of the captured images to a computer that can perform OCR

EDDI_input_formats: example csv files that were given to demonstrate the format that inputs into EDDI must be

bboxImgs: when running test_bboxes.py, it generates images of bounding boxes. These are written into bboxImgs

accuracy_result_csvs: the output of OCR data extraction written into a CSV format. Some of these csvs can be used for accuracy evaluation (if they end in _accuracyChecking) and some can be used as input to EDDI (if they end with _eddi)

MonitorMakingGUI.py: a python file. You provide the path to an image of a monitor, and it makes a GUI that lets the user specify where each physiological parameter is located in the image. Then it writes the data into a json file, and can be loaded as CustomMonitor when running other python files

monitor_values.py: a python file. It contains information of the field layouts of 2 monitors: the one used on 21/05/2024 and the one used in 2022. It also contains data on the field ranges of each physiological parameter

test_bboxes.py: a python file used for creating images that show bounding boxes (eg bounding boxes of parameters specified by a monitor, or made by an OCR model)

test_keystone.py: some code that was used to test using keystone correction to address image warping due to camera perspective. 

write_to_csv.py: a file containing code to write OCR-extracted data into csv. It generates 2 csv files, one used for accuracy checking (that contains results accurate to what text is displayed on the monitor screen) and another that EDDI can use as input

query.py: A file that contains the code for querying OCR AI models (such as EasyOCR), as well as the code for postprocessing their outputs (sanitycheck_data performs postprocessing on OCR output)

process_img.py: Processes an image of the whole monitor screen and returns an array of images of each physiological parameter in the monitor screen, and performs preprocessing to make the images extra-readable for OCR

check_accuracy.py: Can tell you the accuracy of OCR output. It takes a csv as an input and tells you how accurate your OCR data extraction was, and generates several plots

Fake_Images_For_EDDI.py: it will copy images from a specified image folder into images_from_rpi folder
It is used to fake the rpi sending in new images over ssh

main.py: Has several useful functions
get_latest_received_img_data: takes the latest image sent into images_from_rpi, performs OCR on it, and returns the extracted data
write_to_csv_all_images: takes all images in an image folder, performs OCR on all of them, and writes the result into csv files
test_with_random_image and test_with_img: functions to test the accuracy of the OCR on one particular image

## Common tasks you'll want to perform

### Run the project (as a whole, from rpi image capture to EDDI input)

- Make sure images_from_rpi folder is empty
- Attach the rpi to a medical monitor, and connect the rpi to the computer via ssh
- Get networking between computer and rpi working (look at the instructions in Hardware_Use_Instructions.md)
- Send one image captured from the rpi to the computer
- Make the medical monitor display simulated values
- Run 'py MonitorMakingGUI.py' using the one image sent from the rpi. Use it to make a MonitorValues.json file
This will specify for the OCR which parts of the image to read to get image data
- On the rpi, run main.py: this will continually capture images and send them into the images_from_rpi folder
- Launch the EDDI app. (do this by cloning the EDDI repository, going to the OCR branch, and running the app using visual studio)
- In the EDDI repository, adjust pipe_data.py to use a different monitor
(it should use a CustomMonitor. You load it in something like this
``` monitor = CustomMonitor(monitorfile) ``` where monitorFile is the json file you made with MonitorMakingGUI.py )
- In the EDDI repository, run 'py pipe_data.py'. pipe_data.py will run OCR code in main.py that will process the latest image in the images_from_rpi folder and send the data into EDDI.
Wait until it says 'waiting for client to connect'
- In the EDDI app, set the input to OCR. Click "connect"
Wait a few seconds for pipe_data.py to start sending OCR inputs to EDDI
- Click 'apply' in EDDI. EDDI will now be taking inputs from the pipe_data.py pipe. And the inputs from the pipe_data pipe are the outputs of the OCR. And the OCR is from the images in images_from_rpi. And images_from_rpi has images that were captured and sent by the rpi.

### Run the project, without setting up the rpi

- Make sure images_from_rpi folder is empty
- In this repository, run 'py Fake_Images_For_EDDI.py'. This will take images fron normalhospital_images and copy them into images_from_rpi folder
- Follow the other steps (such as running EDDI and pipe_data.py) as normal

### Evaluate OCR accuracy

- Run 'py main.py normalhospital_images HospitalMonitor'
This will generate 2 csv files which have the OCR outputs for each image in normalhospital_images, and will use the monitor HospitalMonitor. One of these csv files will have _accuracyChecking on the end. That's the csv you want to use
- Run 'py check_accuracy.py csv_you_want_to_use NormalHospital HospitalMonitor'
Where csv_you_want_to_use is the csv you want the accuracy for, NormalHospital is the sheet in monitor_data.xslx that has the data for the image folder you used to generate the csv, and HospitalMonitor is the same monitor you used in the step with main.py
This will generate several pyplots to show you things like accuracy