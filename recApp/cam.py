from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.properties import StringProperty, NumericProperty

import cv2
import os

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
    'avi': cv2.VideoWriter_fourcc(*'XVID'),
    # 'mp4': cv2.VideoWriter_fourcc(*'H264'),
    'mp4': cv2.VideoWriter_fourcc(*'XVID'),
}


class KivyCamera(BoxLayout):
    filename = StringProperty('video.avi')
    frames_per_second = NumericProperty(10.0)
    video_resolution = StringProperty('720p')

    def __init__(self, **kwargs):
        super(KivyCamera, self).__init__(**kwargs)
        self.img1 = Image()
        self.b1 = Button()
        self.add_widget(self.img1)
        # self.add_widget(self.b1)
        self.capture = cv2.VideoCapture(0)
        self.out = cv2.VideoWriter(self.filename, self.get_video_type(
            self.filename), self.frames_per_second, self.get_dims(self.capture, self.video_resolution))
        Clock.schedule_interval(self.update, 1 / self.frames_per_second)

    def update(self, *args):
        ret, frame = self.capture.read()
        self.out.write(frame)
        buf = cv2.flip(frame, 0).tostring()
        texture = Texture.create(
            size=(frame.shape[1], frame.shape[0]), colorfmt="bgr")
        texture.blit_buffer(buf, colorfmt="bgr", bufferfmt="ubyte")
        self.img1.texture = texture

    # Set resolution for the video capture
    # Function adapted from https://kirr.co/0l6qmh
    def change_resolution(self, cap, width, height):
        self.capture.set(3, width)
        self.capture.set(4, height)

    # grab resolution dimensions and set video capture to it.
    def get_dims(self, cap, video_resolution='1080p'):
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
        return VIDEO_TYPE['avi']


class CamApp(App):
    def build(self):
        return KivyCamera()


if __name__ == '__main__':
    CamApp().run()
