
# HARDWARE NOTES

## Instructions to run the raspberry pi

- connect keyboard and mouse to 2 usb ports on the end of the rpi.
- Connect the pi to a monitor for display. There are 2 options:
  - use a DVI-to-hdmi cable to connect pi to a monitor (some monitors have a DVI port at the back)
  - use a hdmi-to-hdmi cable to connect pi to a monitor
- set the input of monitor to correct format (eg VGA) so that it will display the input from the rpi, when the rpi is powered on
- connect rpi to power using the usb-c power port on the side. This will turn the pi on. There is no on/off switch needed.
The pi should boot up (you can tell because the red light turns on)
- If you can't see anything on your screen, turn the rpi off and on again, after having ensured that all other steps were done correctly.
Doing something like connecting the monitor after having turned the pi on first will sometimes lead to the monitor not displaying correctly.

If the .bashrc has been set up to automatically run the image capture code, after finishing booting (a lot of text will scroll by on the monitor) the pi will display this text repeatedly:

```text
Image number X captured
Time taken for image capture: Y
Time between beginning of each image capture: 10.0
```

This is the program main.py running and taking images

## To look at the code within the raspberry pi and access the GUI

- (if the .bashrc has been setup) enter ctrl-c to stop the program from running
- enter startx, and press enter to start the GUI
- navigate to the code using the file explorer (eg home/engr302t12/Documents/optical-character-recognition/Project_Code). main.py is the python file that was running on startup. The folders named "images" with a timestamp will store all images that were taken while main.py was running.
- When creating a new terminal, if .bashrc is setup to automatically run main.py, you will need to press ctrl-c each time you enter a terminal to stop main.py from running.
It is also recommend that you stop all currently running python programs from running, in terminal enter pkill -f python
- To run any python program, you cannot use geany to run python (it has errors recognizing which packages are present).
You need to make a new terminal and run python main.py
- Remember to take the cap off the camera so that images can be seen

## To adjust camera focus

- On the camera, twist the lens clockwise or counterclockwise to adjust the focus. Twisting counterclockwise brings the focus closer, twisting clockwise pushes the focus further out.

## To add files onto the raspberry pi

You can use the internet to transfer files, but this is extremely slow.
It is recommended to use a USB stick to transfer files.

## Installing python versions/packages

To install python packages, use Pip. Please note it is slow due to its reliance on the rpi's internet connection.

To install a different python version, follow the instructions present in https://hub.tcno.co/pi/software/python-update/.
I recommend when running sudo make to use one core instead of 4 to avoid crashes.

## Test whether the system is 32 bit or 64 bit

- Open a terminal
- Enter "python"
- Enter "import struct"
- enter "print(struct.calcsize("P") * 8)
- It will print out 32 or 64

## To set up the raspberry pi from a blank installation

For 32 bit image capturing:

These steps assume that you have already removed the RPI SD card and installed/reinstalled a 32 bit OS on it.

- Copy the files within the Code_For_Image_Capture_(32_bit) folder onto the rpi, using a USB. Put them in a folder you will remember where it is. The files you have copied over should be app.py and main.py, and they should be in the same directory.
- If you wish to set up a virtual environment, use virtualenv to set it up
- Install the needed packages using pip (it is recommended you use a terminal and run 'python main.py' and address any errors to make sure all needed packages are installed)
- If you wish to have main.py run automatically on startup, within the home directory (whichever directory the file explorer shows has an icon of a red home on it - or whichever directory you navigate to with 'cd ~') modify the .bashrc file (use 'nano .bashrc' to modify .bashrc) to have the instructions at the bottom (before the virtual enviromnent's environment variables are exported, but after everything else)

```bash
source ~/path/to/virtualenvironment/bin/activate
cd ~/path/to/folder_containing_main.py
python main.py
```

### Problems with the hardware that will need to be avoided/worked around

- The camera cable is exposed - be careful with it.
- The camera can fall off the end of it's extendable stick, so be careful with which angle you hold the hardware at.
- The camera zoom can shift if you're not careful
- The hardware has 2 screwing clamps that are used to attach the camera to monitors. Each of these has a 'foot' on the end.
Be careful, because these feet can easily break off.
- The Raspberry pi has a 3d printed box all around it. Be aware that this box may be too small to allow certain plugs to connect.
For example, one wide adapter for a DVI-to-hdmi cable was unable to fully fit into the raspberry pi's hdmi port.
