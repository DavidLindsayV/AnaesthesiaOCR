import json
import sys
import tkinter as tk
from tkinter import Button, Canvas
from PIL import Image, ImageTk

class ImageClickApp:
    """The GUI to create the JSON file so that a Monitor can be used that knows what pixel positions to read physiological parameters from images of a monitor
    """
    def __init__(self, root, image_path):
        self.root = root
        self.root.title("Field Position Measurer")

        # Load the image
        self.image = Image.open(image_path)
        self.image = self.image.transpose(Image.FLIP_TOP_BOTTOM)
        self.image = self.image.transpose(Image.FLIP_LEFT_RIGHT)

        self.tk_image = ImageTk.PhotoImage(self.image)

        # Create a canvas widget to display the image
        self.canvas = Canvas(root, width=self.image.width, height=self.image.height)
        self.canvas.pack()

        # Display the image on the canvas
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

        # Bind mouse events to track clicks and releases
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

        # Variables to store click and release positions
        self.click_pos = None
        self.release_pos = None

        self.button_frame = tk.Frame(root)
        self.button_frame.pack(side=tk.BOTTOM)

        # Add a button to clear the canvas
        self.field_buttons = []
        num_columns = 10
        field_names = ["ecg.hr", "co2.et", "co2.fi", "co2.rr", "p1.sys", "p1.dia", "p1.mean", "aa.et", "aa.fi", "spo2.SpO2", "spo2.pr"]
        # field_names = ["ecg.hr","p1.sys",	"p1.dia",	"p1.mean",	"p1.hr",	"nibp.sys",	"nibp.dia",	"nibp.mean",	"nibp.hr",	"t1.temp",	"t2.temp",	"t3.temp",	"t4.temp",	"spo2.SpO2"	,"spo2.pr",	"spo2.ir_amp",	"co2.et",	"co2.fi",	"co2.rr",	"co2.amb_press",	"o2.et",	"o2.fi",	"n2o.et",	"n2o.fi",	"aa.et",	"aa.fi",	"aa.mac_sum",	"p5.sys",	"p5.dia",	"p5.mean",	"p5.hr",	"p6.sys",	"p6.dia",	"p6.mean",	"p6.hr"]
        for i, field_name in enumerate(field_names):
            button = Button(self.button_frame, text=field_name, command=lambda field_name=field_name: self.set_field(field_name=field_name))
            # button.pack(side=tk.LEFT, padx=0, pady=0)
            row = i // num_columns
            col = i % num_columns
            button.grid(row=row, column=col, padx=10, pady=10)
            self.field_buttons.append(button)

        self.finished_button = Button(self.button_frame, text="Export Values", command=self.write_monitor_values)
        self.finished_button.grid(row=len(field_names)//num_columns + 1, column=0, padx=10, pady=10)


        self.monitor_values = {}

    def on_click(self, event):
        # Record the position where the mouse was clicked
        self.click_pos = (event.x, event.y)
        print(f"Mouse clicked at: {self.click_pos}")

    def on_release(self, event):
        # Record the position where the mouse was released
        self.release_pos = (event.x, event.y)
        print(f"Mouse released at: {self.release_pos}")
        self.canvas.create_rectangle(self.click_pos[0], self.click_pos[1], self.release_pos[0], self.release_pos[1], outline="blue", width=2)
        self.canvas.create_text(self.click_pos[0], self.click_pos[1], text=self.field_name, font=("Arial", 10), fill="red")
        self.monitor_values[self.field_name] = (self.click_pos[0], self.click_pos[1], self.release_pos[0], self.release_pos[1])

    def set_field(self, field_name):
        self.field_name = field_name

    def write_monitor_values(self):
        with open("MonitorValues.json", "w") as file:
            json.dump(self.monitor_values, file)
            print("The monitor values have been written to MonitorValues.json. You can now close the GUI")

if __name__ == "__main__":
    """Makes a GUI to create a json file to specify what pixel coordinates need to be used to read from an image
    """
    if len(sys.argv) == 2:
        # Initialize the Tkinter window
        root = tk.Tk()


        # Path to your image
        image_path = sys.argv[1]

        # Create the application
        app = ImageClickApp(root, image_path)

        # Start the Tkinter main loop
        root.mainloop()
    else:
        print(
            "Need to enter 1 cmd argument: The path to the image that you want to use to determine the positions for each field on the monitor"
        )
