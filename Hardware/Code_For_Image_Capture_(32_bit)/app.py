"""This module holds the App class"""

import time
from cv2 import cv2 as cv
import queue
import os
import threading
import subprocess

class VidCapture:
	def __init__(self, name):
		self.cap = cv.VideoCapture(name)
		self.q = queue.Queue()
		t = threading.Thread(target=self._reader)
		t.daemon = True
		t.start()
	
	def _reader(self):
		while True:
			ret, frame = self.cap.read()
			if not ret:
				break
			if not self.q.empty():
				try:
					self.q.get_nowait()
				except Queue.empty():
					pass
			self.q.put(frame)
		
	def read(self):
		return self.q.get()
		

class App:
    """App is the main class that instantiates the Output and Pipeline.

    This class contains a Pipeline and an Output, once run() is called,
    it takes a picture, reads it, processes it through the Pipeline and
    writes the result to Output.
    If stop() is called while the App is running, it will stop the program.

    Attributes:
        pipeline: A Pipeline to process the images
        out: An abstract Output to write to its underlying stream
        start_time: the time App was initialized
        max_cycles: the maximum number of cycles, -1 indicates infinity
        cycles: the current cycle count
        delay: the number of seconds in a cycle
        image: the image to process
    """


    def __init__(self, IP, password, max_cycles=-1, delay=10):
        """Initialize the App and relevant class fields.

        Args:
            max_cycles: maximum number of cycles for this App
            delay: delay for this App
            image: the image to process
        """
        self.start_time = 0
        self.max_cycles = max_cycles
        self.cycles = 0
        self.delay = delay
        self.IP = IP;
        self.password = password
	
    def send_image(self, imagename):
            remote_user = "david"
            remote_host = self.IP
            remote_folder = "C:/Users/david/Documents/University_courses/University_2024_Tri1/ENGR489/engr489-anaesthesiaocr/images_from_rpi"
            command = f"sshpass -p {self.password} scp ./{imagename} {remote_user}@{remote_host}:{remote_folder}" 
            try:
                result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
            except subprocess.CalledProcess as e:
                print("error sending images over ssh")
                print(e.stderr.decode())


    def run(self):
        """Run and process for max_cycles then close.

        Every cycle, this method takes a picture, reads it,
        processes it through the Pipeline and then writes the result to Output.
        Cycles consist of 10 seconds and once it has done this process,
        it sleeps for the remainder of the cycle.
        This loops for max_cycles or infinitely if max_cycles is -1.
        """
        
        self.start_time = time.perf_counter()
        cap = VidCapture(0)
        count = 0
        ocr_data = []
        os.mkdir("images-" + str(self.start_time))
        begin_image_capture_time = self.start_time
	
        while self.max_cycles == -1 or self.cycles < self.max_cycles:
            count += 1
            image = cap.read()
            imagename = 'images-' + str(self.start_time) + '/'+str(count)+'tmp.jpg'
            cv.imwrite(imagename, image)
	    
	    #Send image to PC via ssh
            self.send_image(imagename)
            end_image_capture_time = time.perf_counter()
	    
            # Sleep rest of cycle
            current_time = time.perf_counter()
            wait_time = self.delay - (current_time - self.start_time) % self.delay
            time.sleep(wait_time)
            # Debug info
            print("Image number " + str(count) + " captured")
            print(f"""Time taken for image capture and sending over ssh: {(end_image_capture_time - begin_image_capture_time):.2f}""")
            print(f"""Time  between beginning of each image capture: {(time.perf_counter() - begin_image_capture_time):.1f}\n\n""")
            begin_image_capture_time = time.perf_counter()
	    
            if self.max_cycles != -1:
                self.cycles += 1
                if self.cycles == self.max_cycles:
                    return ocr_data
        cap.release()
        cv.destroyAllWindows()
