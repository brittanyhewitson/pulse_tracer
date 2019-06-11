import cv2
import click
import numpy as np
import matplotlib.pyplot as plt

from scipy import signal


@click.command()
@click.argument("filename", nargs=1)
def process_video(filename):
    video = cv2.VideoCapture(filename)

    while(True):
        ret, frame = video.read()
        if frame is None:
            break
        
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # When everything done, release the capture
    video.release()
    cv2.destroyAllWindows()

if __name__=="__main__":
    process_video()

