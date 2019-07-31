import sys
import cv2
import dlib
import click
import json
import logging
import numpy as np
import matplotlib.pyplot as plt

from math import floor, sqrt
from datetime import datetime

# Set up logging
LOGGING_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(format=LOGGING_FORMAT, stream=sys.stderr, level=logging.INFO)

TRAINED_XMLS = [
    '../data/haarcascade_frontalface_default.xml',
    '../data/haarcascade_frontalface_alt.xml',
    '../data/haarcascade_frontalface_alt2.xml',
    '../data/haarcascade_profileface.xml'
]


class ProcessStream(object):
    def __init__(self):
        pass


class ProcessVideo(object):
    def __init__(self, filename):
        self.predictor = dlib.shape_predictor("../data/shape_predictor_68_face_landmarks.dat")
        self.video = cv2.VideoCapture(filename)  
        self.trained_classifiers = []
        self.colors = [
            (0, 255, 0),  # Green
            (255, 0, 0),  # Blue
            (0, 0, 255),  # Red
            (255, 0, 255) # Magenta
        ]
        for trained_xml in TRAINED_XMLS:
            self.trained_classifiers.append(cv2.CascadeClassifier(trained_xml))
        self.rois = []
        self.frame_time = 0
        self.frame = []
        self.gray_image = []
        self.batch_id = ""

    def rotate_image(self):
        rows, cols, color = self.frame.shape
        M = cv2.getRotationMatrix2D((cols/2, rows/2), 270, 1)
        frame = cv2.warpAffine(self.frame, M, (cols, rows))
        return frame

    def draw_rectangle(self, faces, color):
        for (x, y, w, h) in faces:
            cv2.rectangle(self.frame, (x, y), (x+w, y+h), color, 2)

    def detect_faces(self):
        for i in range(len(self.trained_classifiers)):
            faces = self.trained_classifiers[i].detectMultiScale(
                self.gray_image, 
                scaleFactor=1.1,
                minNeighbors=5, 
                minSize=(100, 100)
            )
            # Break if a face is recognized
            if len(faces) > 0:
                break

        # Return nothing if no face could be detected for this frame
        if len(faces) == 0:
            return faces

        # Draw the detected face
        self.draw_rectangle(faces, self.colors[i])
        return faces

    def get_roi(self, landmarks, landmark_range, roi_side, vert_translation, hor_translation):
        for n in landmark_range:
            x_n = landmarks.part(n).x
            y_n = landmarks.part(n).y
            cv2.circle(self.frame, (x_n, y_n), 2, (255, 0, 0), -1)

            x1 = x_n + hor_translation + roi_side
            x2 = x_n + hor_translation - roi_side
            y1 = y_n + vert_translation + roi_side
            y2 = y_n + vert_translation - roi_side
            cv2.rectangle(self.frame, (x1, y1), (x2, y2), (255, 255, 0), 2)

            roi = {
                'batch_id': self.batch_id,
                'collection_time': self.frame_time,
                'location_id': n,
                'red_data': self.frame[x2:x1, y2:y1, 2].tolist(),
                'green_data': self.frame[x2:x1, y2:y1, 1].tolist(),
                'blue_data': self.frame[x2:x1, y2:y1, 0].tolist()
            }
            if n in self.roi_locations:
                self.rois.append(roi)

    def get_landmarks(self, faces, roi_locations):
        self.roi_locations = roi_locations
        for (x, y, w, h) in faces:
            face = dlib.rectangle(x, y, w+x, h+y)
            landmarks = self.predictor(self.gray_image, face)

            # Determine the size of the ROI based on the detected face
            roi_area = 0.005 * face.area()
            roi_side = floor(sqrt(roi_area)/2)
            forehead_vert_translation = roi_side
            cheek_hor_translation = floor(sqrt(0.05 * face.area())/2)

            # Get the ROI for the nose
            self.get_roi(
                landmarks, 
                range(27, 31),
                roi_side, 
                forehead_vert_translation,
                0
            )
        
            # Get the ROI for the forehead
            self.get_roi(
                landmarks, 
                range(17, 27),
                roi_side, 
                -forehead_vert_translation,
                0
            )

            # Get the ROI for the left cheek
            self.get_roi(
                landmarks, 
                range(31, 32),
                roi_side, 
                0,
                -cheek_hor_translation
            )

            # Get the ROI for the right cheek
            self.get_roi(
                landmarks, 
                range(35, 36),
                roi_side,
                0,
                cheek_hor_translation
            )
            break
            