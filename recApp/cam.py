from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.graphics import Ellipse, Color
from kivy.properties import ObjectProperty, StringProperty, NumericProperty
from kivy.config import Config

import cv2
import os

import datetime

# 0 being off 1 being on as in true / false
# you can use 0 or 1 && True or False
Config.set("graphics", "resizable", "0")

# fix the width of the window
Config.set("graphics", "width", "800")

# fix the height of the window
Config.set("graphics", "height", "480")

# Standard Video Dimensions Sizes
STD_DIMENSIONS = {
    "480p": (640, 480),
    "720p": (1280, 720),
    "1080p": (1920, 1080),
    "4k": (3840, 2160),
}

# Video Encoding, might require additional installs
# Types of Codes: http://www.fourcc.org/codecs.php
VIDEO_TYPE = {
    "avi": cv2.VideoWriter_fourcc(*"XVID"),
    # 'mp4': cv2.VideoWriter_fourcc(*'H264'),
    "mp4": cv2.VideoWriter_fourcc(*"XVID"),
}

class Circle(Widget):
    def __init__(self, **kwargs):
        super(Circle, self).__init__(**kwargs)
#        with self.canvas:
#            Color(1, 0, 0, 1)
#            self.dot = Ellipse(pos=(765, 434), size=(20, 20))
    def blink(self):
        self.canvas.clear()
        with self.canvas:
            print('blink')
            Color(0, 0, 0, 1)
            Ellipse(pos=(765, 434), size=(20, 20))

class KivyCamera(FloatLayout):
#    circle = Circle()
    recording = True
    indicator_visible = True
    frames_per_second = NumericProperty(10.0)
    video_resolution = StringProperty("720p")
    frame_box = ObjectProperty()
    toggle_rec_text = StringProperty("stop")


    def __init__(self, **kwargs):
        super(KivyCamera, self).__init__(**kwargs)
        self.filename = self.gen_filename()

        self.indicator_interval= 0.8

        self.capture = cv2.VideoCapture(0)
        self.out = cv2.VideoWriter(
            "videos/" + self.filename,
            self.get_video_type(self.filename),
            self.frames_per_second,
            self.get_dims(self.capture, self.video_resolution),
        )
        Clock.schedule_interval(self.update_indicator, self.indicator_interval)
        Clock.schedule_interval(self.update, 1 / self.frames_per_second)

    def update(self, *args):
        ret, frame = self.capture.read()
        self.out.write(frame)
        buf = cv2.flip(frame, 0).tobytes()
        texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt="bgr")
        texture.blit_buffer(buf, colorfmt="bgr", bufferfmt="ubyte")
        self.frame_box.texture = texture
        # self.canvas.ask_update()

    # Set resolution for the video capture
    # Function adapted from https://kirr.co/0l6qmh

    def change_resolution(self, cap, width, height):
        self.capture.set(3, width)
        self.capture.set(4, height)

    # grab resolution dimensions and set video capture to it.
    def get_dims(self, cap, video_resolution="1080p"):
        width, height = STD_DIMENSIONS["480p"]
        if self.video_resolution in STD_DIMENSIONS:
            width, height = STD_DIMENSIONS[self.video_resolution]
        # change the current capture device
        # to the resulting resolution
        self.change_resolution(cap, width, height)
        return width, height

    def get_video_type(self, filename):
        filename, ext = os.path.splitext(filename)
        if ext in VIDEO_TYPE:
            return VIDEO_TYPE[ext]
        return VIDEO_TYPE["avi"]

    def toggle_recording(self):
        if self.recording:
            Clock.unschedule(self.update)
            Clock.unschedule(self.update_indicator)
            self.toggle_rec_text = "start"
            self.out.release()
            self.indicator.background_color = (1, 0, 0, 0)
        else:
            self.filename = self.gen_filename()
            self.out = cv2.VideoWriter(
                "videos/" + self.filename,
                self.get_video_type(self.filename),
                self.frames_per_second,
                self.get_dims(self.capture, self.video_resolution),
            )
            Clock.schedule_interval(self.update, 1 / self.frames_per_second)
            Clock.schedule_interval(self.update_indicator, self.indicator_interval)
            self.toggle_rec_text = "stop"
        self.recording = not self.recording

    def update_indicator(self, *args):
        if self.indicator_visible:
            self.indicator.background_color = (1, 0, 0, 0)
        else:
            self.indicator.background_color = (1, 0, 0, 1)
        self.indicator_visible = not self.indicator_visible

    def gen_filename(self):
        return datetime.datetime.now().strftime("%m-%d--%H-%M-%S.avi")

    def on_touch_down(self, touch):
        print(touch.x)
        print(touch.y)
        if touch.x > 700 and touch.y < 80:
            self.toggle_recording()
        #0.878598, 0.162839
        #if self.button.collide_point(*touch.pos):
        #    print('insdie')
        #    # The touch has occurred inside the widgets area. Do stuff!
        #    pass

class CamApp(App):
    def build(self):
        return KivyCamera()


if __name__ == "__main__":
    CamApp().run()
