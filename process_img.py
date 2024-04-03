from PIL import Image, ImageEnhance, ImageFilter

import os

def resize_height(image, ideal_height):
    return image.resize((int(image.width/image.height * ideal_height), ideal_height))

def get_parameter_imgs(modified_image):
    #parameters = 
    # rtime	ecg.hr	ecg.st1	ecg.st2	ecg.st3	ecg.imp_rr	p1.sys	p1.dia	p1.mean	p1.hr	p2.sys	p2.dia	p2.mean	p2.hr	p3.sys	p3.dia	p3.mean	p3.hr	p4.sys	p4.dia	p4.mean	p4.hr	nibp.sys	nibp.dia	nibp.mean	nibp.hr	t1.temp	t2.temp	t3.temp	t4.temp	spo2.SpO2	spo2.pr	spo2.ir_amp	co2.et	co2.fi	co2.rr	co2.amb_press	o2.et	o2.fi	n2o.et	n2o.fi	aa.et	aa.fi	aa.mac_sum	p5.sys	p5.dia	p5.mean	p5.hr	p6.sys	p6.dia	p6.mean	p6.hr

    #Get a subsection that is the heart rate
    heartrate_image = modified_image.crop((500, 160, 580, 230))  #TODO ask Michael how many digits each of these can be, and whether the number of digits changes their positions
    #ecto2
    ecto2_image = modified_image.crop((465, 330, 510, 365))
    #fico2
    fico2_image = modified_image.crop((470, 365, 500, 390)) 
    #rr
    rr_image = modified_image.crop((500, 360, 530, 390)) 
    #systolic pressure
    sys_psi_image = modified_image.crop((410, 400, 470, 430)) 
    #diastolic pressure
    dias_psi_image = modified_image.crop((480, 400, 530, 430)) 
    #arterial pressure
    art_psi_image = modified_image.crop((423, 430, 460, 450)) 
    #anaes concentration 1
    ana_conc1_image = modified_image.crop((115, 400, 160, 425)) 
    # anaes concentration 2  
    ana_conc2_image = modified_image.crop((120, 425, 160, 445)) 

    imageDict = {'ecg.hr':heartrate_image, 'co2.et':ecto2_image, 'co2.fi':fico2_image, 'co2.rr':rr_image, 'p1.sys':sys_psi_image, 'p1.dia':dias_psi_image, 'p1.mean':art_psi_image, 'n2o.et': ana_conc1_image, 'n2o.fi': ana_conc2_image}

    ideal_height = 100
    for key in imageDict.keys():
        #Resize the images so all text is of a usable size
        imageDict[key] = resize_height(imageDict[key], ideal_height)

        #Convert to greyscale
        imageDict[key] = imageDict[key].convert("L")

        # # Enhance contrast
        # contrast_enhancer = ImageEnhance.Contrast(imageDict[key])
        # imageDict[key] = contrast_enhancer.enhance(20)  # Increase contrast (adjust as needed)
        
        # # Enhance sharpness
        sharpness_enhancer = ImageEnhance.Sharpness(imageDict[key])
        imageDict[key] = sharpness_enhancer.enhance(20.0)  # Increase sharpness (adjust as needed)

        #Save the images
        imageDict[key].save(os.path.join("processed_images", key + "-img.png"))

    return imageDict
    


def process_img(imgName):
    image = Image.open(imgName)

    #Get image in the right orientation
    modified_image = image.transpose(Image.FLIP_TOP_BOTTOM)
    modified_image = modified_image.transpose(Image.FLIP_LEFT_RIGHT)

    modified_image.save(os.path.join("processed_images", imgName))

    #Denoise image
    # open_cv_image = numpy.array(modified_image)
    # modified_image = cv2.fastNlMeansDenoisingColored(open_cv_image)  #this denoising did nothing. But this function can take extra arguments so maybe denoising can be improved
    # modified_image = Image.fromarray(open_cv_image)

    #Make image greyscale 
    # modified_image = modified_image.convert('L')

    return get_parameter_imgs(modified_image)