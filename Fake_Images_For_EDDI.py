from datetime import datetime
import shutil
import os
import time

def fake_image_capture_for_EDDI():
    """Continually copies images from one of the image datasets into images_from_rpi, to simulate new images being captured and sent from the raspberry pi
    It's used to simulate new images being captured without needing access to a medical simulator
    """
    
    count = 1
    while(True):
        starttime = datetime.now()
        shutil.copy(os.path.join("images", "normalhospital_images", str(count) + "tmp.jpg"), "images_from_rpi")
        print("Copied img " + str(count) + "tmp.jpg")
        count += 1
        timetaken = (datetime.now() - starttime).total_seconds()
        time.sleep(10 - timetaken)

if __name__ == "__main__":
    fake_image_capture_for_EDDI()