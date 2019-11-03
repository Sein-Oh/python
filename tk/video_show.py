import cv2
import PIL.Image, PIL.ImageTk
from tkinter import *

class App:
    def __init__(self, window):
        self.window = window
        self.window.title("Tkinter + OpenCV")
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        self.canvas = Canvas(window, width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH), height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.canvas.pack()

        self.delay = 33
        self.update()
        self.window.mainloop()

    def update(self):
        ret, frame = self.cap.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        if ret:
            self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
            self.canvas.create_image(0, 0, image = self.photo, anchor = NW)

        self.window.after(self.delay, self.update)


App(Tk())
