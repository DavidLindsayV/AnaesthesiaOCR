
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

After finishing booting (a lot of text will scroll by on the monitor) the pi will display this text repeatedly:

```text
True
Time Taken:
                  10.0
```

This is the program main.py running and taking images

## To look at the code within the raspberry pi and access the GUI

- enter ctrl-c to stop the program from running
- enter startx, and press enter to start the GUI
- within the main directory you will see python files, eg main.py, app.py. main.py is the python file that was running on startup. The images directory will store all images that were taken while main.py was running.
- To stop all python programs from running, in terminal enter pkill -f python
- To run any python program, you cannot use geany (it has errors recognizing which packages are present).
  You need to make a new terminal and run python main.py
- Remember to take the cap off the camera so that images can be seen

## To adjust camera focus

- On the camera, twist the lens clockwise or counterclockwise to adjust the focus. Twisting counterclockwise brings the focus closer, twisting clockwise pushes the focus further out.

## To add files onto the raspberry pi

You can use the internet to transfer files, but this is extremely slow.
It is recommended to use a USB stick to transfer files.

## Installing python versions/packages

To install python packages, use Pip. Please note it is slow due to its reliance on the rpi's internet connection.

To install a different python version, follow the instructions present in https://hub.tcno.co/pi/software/python-update/ 

### Problems with the hardware that will need to be avoided/worked around

- The camera cable is exposed - be careful with it.
- The camera can fall off the end of it's extendable stick, so be careful with which angle you hold the hardware at.
- The camera zoom can shift if you're not careful
- The hardware has 2 screwing clamps that are used to attach the camera to monitors. Each of these has a 'foot' on the end.
Be careful, because these feet can easily break off.
- The Raspberry pi has a 3d printed box all around it. Be aware that this box may be too small to allow certain plugs to connect.
For example, one wide adapter for a DVI-to-hdmi cable was unable to fully fit into the raspberry pi's hdmi port.
