from picamera import PiCamera
from time import sleep

camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
camera.start_preview()
camera.start_recording('wo_blindfold.h264')
sleep(30)
camera.stop_recording();
camera.stop_preview()
