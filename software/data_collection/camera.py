#pip install "picamera[array]"
from picamera import PiCamera
from time import sleep

camera = PiCamera()
camera.rotation = 180
camera.resolution = (640, 480)
camera.framerate = 32
camera.start_preview()
camera.start_recording('100mW1m.h264')
sleep(20)
camera.stop_recording();
camera.stop_preview()
