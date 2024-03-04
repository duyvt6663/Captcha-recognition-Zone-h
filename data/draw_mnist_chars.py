import tkinter as tk
from tkinter import simpledialog
from PIL import Image, ImageDraw
import uuid
import os

# Parameters
canvas_width = 280
canvas_height = 280
image_size = (50, 50)
save_path = "mnist_chars/"

class DrawingApp:
    def __init__(self, master):
        self.master = master
        self.brush_size = 17
        self.brush_color = "black"
        self.canvas = tk.Canvas(master, bg="white", width=canvas_width, height=canvas_height)
        self.canvas.pack()

        self.image = Image.new("L", (canvas_width, canvas_height), "white")
        self.draw = ImageDraw.Draw(self.image)

        self.setup()
        self.create_widgets()

    def setup(self):
        self.old_x = None
        self.old_y = None
        self.line_width = self.brush_size
        self.color = self.brush_color
        self.canvas.bind('<B1-Motion>', self.paint)
        self.canvas.bind('<ButtonRelease-1>', self.reset)

    def paint(self, event):
        paint_color = self.color
        if self.old_x and self.old_y:
            self.canvas.create_line(self.old_x, self.old_y, event.x, event.y,
                               width=self.line_width, fill=paint_color,
                               capstyle=tk.ROUND, smooth=tk.TRUE, splinesteps=36)
            self.draw.line([self.old_x, self.old_y, event.x, event.y], fill="black", width=self.line_width)

        self.old_x = event.x
        self.old_y = event.y

    def reset(self, event):
        self.old_x = None
        self.old_y = None

    def clear_canvas(self):
        self.canvas.delete("all")
        self.image = Image.new("L", (canvas_width, canvas_height), "white")
        self.draw = ImageDraw.Draw(self.image)

    def save_image(self):
        filefolder = simpledialog.askstring("Input", "Enter character:", parent=self.master)
        # make sure the input is a single uppercase letter
        if filefolder and filefolder.isalpha() and filefolder.isupper() and len(filefolder) == 1:
            if not os.path.exists(save_path + filefolder):
                os.makedirs(save_path + filefolder)

            # Resize and save image inside the folder
            resized_image = self.image.resize(image_size, Image.LANCZOS)
            # new file name using uuid
            file_name = "img_" + str(uuid.uuid4()) + ".png"
            file_path = save_path + filefolder + "/" + file_name
            resized_image.save(file_path)
        else:
            print("Invalid input. Please enter a single uppercase letter.")

    def create_widgets(self):
        self.controls_frame = tk.Frame(self.master)
        self.controls_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.clear_button = tk.Button(self.controls_frame, text="Clear", command=self.clear_canvas)
        self.clear_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.enter_button = tk.Button(self.controls_frame, text="Save", command=self.save_image)
        self.enter_button.pack(side=tk.LEFT, padx=5, pady=5)

if __name__ == '__main__':
    root = tk.Tk()
    root.attributes("-alpha", 0.5)
    root.title("MNIST Digit Drawer")
    app = DrawingApp(root)
    root.mainloop()