import sys
import cv2
import click
import timeit
import logging
import numpy as np
import matplotlib.pyplot as plt

from scipy import signal

# Set up logging
LOGGING_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(format=LOGGING_FORMAT, stream=sys.stderr, level=logging.INFO)

def convertToRGB(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

@click.command()
@click.argument("filename", nargs=1)
def process_video(filename):
    logging.info("Reading video file")
    video = cv2.VideoCapture(filename)
    
    start = timeit.default_timer()
    while(True):
        ret, frame = video.read()
        if frame is None:
            break

        # detect the face
        #logging.info("Detecting facial features")
        haar_cascade_face = cv2.CascadeClassifier('data/haarcascade_frontalface_default.xml')
        gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces_rect = haar_cascade_face.detectMultiScale(gray_image, scaleFactor=1.1, minNeighbors=5)
        for (x, y, w, h) in faces_rect:
            logging.debug(faces_rect)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 15)

        cv2.imshow('frame', frame)
        
        # Break if the "q" key is selected
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    stop = timeit.default_timer()
    total_time = stop - start
    print("Total time was %s" % total_time)
    # When everything done, release the capture
    video.release()
    cv2.destroyAllWindows()

if __name__=="__main__":
    process_video()

