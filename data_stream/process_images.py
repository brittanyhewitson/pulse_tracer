import os
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

from templates import (
    LOGGING_FORMAT,
    TIMEZONE,
    SOFTWARE_DIR,
    ROI_NUM_TO_WORD_MAP
)

# Set up logging
logging.basicConfig(format=LOGGING_FORMAT, stream=sys.stderr, level=logging.INFO)


class Process(object):
    def __init__(self, preprocess_analysis):
        self.device = ""
        self.predictor = dlib.shape_predictor(os.path.join(SOFTWARE_DIR, "data/shape_predictor_68_face_landmarks.dat"))
        self.model = cv2.dnn.readNetFromCaffe(
            os.path.join(SOFTWARE_DIR,'data/deploy.prototxt.txt'), 
            os.path.join(SOFTWARE_DIR,'data/res10_300x300_ssd_iter_140000.caffemodel')
        )
        self.colors = [
            (0, 255, 0),  # Green
            (255, 0, 0),  # Blue
            (0, 0, 255),  # Red
            (255, 0, 255) # Magenta
        ]
        self.rois = []
        self.frame_time = 0
        self.frame = []
        self.gray_image = []
        self.batch_id = ""
        self.preprocess_analysis = preprocess_analysis 

    def rotate_image(self):
        rows, cols, color = self.frame.shape
        M = cv2.getRotationMatrix2D((cols/2, rows/2), 270, 1)
        frame = cv2.warpAffine(self.frame, M, (cols, rows))
        return frame

    def draw_rectangle(self, faces, color):
        for (x, y, w, h) in faces:
            cv2.rectangle(self.frame, (x, y), (x+w, y+h), color, 2)

    def detect_faces(self):
        (h, w) = self.frame.shape[:2]
        
        # BGR
        red_mean = np.array(self.frame[:, :, 2]).mean()
        green_mean = np.array(self.frame[:, :, 1]).mean()
        blue_mean = np.array(self.frame[:, :, 0]).mean()

        blob = cv2.dnn.blobFromImage(
            image=cv2.resize(self.frame, (300, 300)), 
            scalefactor=1.0,
		    size=(300, 300), 
            mean=(red_mean, green_mean, blue_mean)
        )

        self.model.setInput(blob)
        detections = self.model.forward()

        faces = []
        for i in range(0, detections.shape[2]):
            lower_confidence = 0.5
            # extract the confidence of the prediction
            confidence = detections[0, 0, i, 2]

            # filter out weak detections 
            if confidence < lower_confidence:
                continue

            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (x0, y0, x1, y1) = box.astype("int")
            faces.append([x0, y0, x1, y1])

            # draw the bounding box of the face along with the associated
            # probability
            text = "{:.2f}%".format(confidence * 100)
            y = y0 - 10 if y0 - 10 > 10 else y0 + 10
            cv2.rectangle(
                self.frame, 
                (x0, y0), 
                (x1, y1),
                (0, 0, 255), 
                2
            )
            cv2.putText(
                self.frame, 
                text, 
                (x0, y),
                cv2.FONT_HERSHEY_SIMPLEX, 
                0.45, 
                (0, 0, 255), 
                2
            )
            return faces

    def get_roi(self, landmarks, landmark_range, roi_side, vert_translation, hor_translation, batch_id):
        for n in landmark_range:
            x_n = landmarks.part(n).x
            y_n = landmarks.part(n).y
            if x_n >= 640 or y_n >= 480:
                continue
            cv2.circle(self.frame, (x_n, y_n), 2, (255, 0, 0), -1)

            # TODO: ADD ERROR CHEKCING IF COORDINATE IS OUT OF FRAME
            if self.preprocess_analysis == "MD":
                roi = {
                    'batch': batch_id,
                    'collection_time': self.frame_time,
                    'location_id': n,
                    'red_data': str(self.frame[x_n, y_n, 2]),
                    'green_data': str(self.frame[x_n, y_n, 1]),
                    'blue_data': str(self.frame[x_n, y_n, 0])
                }
                if n in self.roi_locations:
                    self.rois.append(roi)

            else:
                x1 = x_n + hor_translation + roi_side
                x2 = x_n + hor_translation - roi_side
                y1 = y_n + vert_translation + roi_side
                y2 = y_n + vert_translation - roi_side
                cv2.rectangle(self.frame, (x1, y1), (x2, y2), (255, 255, 0), 2)

                roi = {
                    'batch': batch_id,
                    'collection_time': self.frame_time,
                    'location_id': n,
                    'red_data': self.frame[x2:x1, y2:y1, 2].tolist(),
                    'green_data': self.frame[x2:x1, y2:y1, 1].tolist(),
                    'blue_data': self.frame[x2:x1, y2:y1, 0].tolist()
                }
                if n in self.roi_locations:
                    self.rois.append(roi)

    def get_landmarks(self, faces, roi_locations, batch_id):
        self.roi_locations = roi_locations
        for (x0, y0, x1, y1) in faces:
            face = dlib.rectangle(x0, y0, x1, y1)
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
                0,
                batch_id
            )
        
            # Get the ROI for the forehead
            self.get_roi(
                landmarks, 
                range(17, 27),
                roi_side, 
                -forehead_vert_translation,
                0,
                batch_id
            )

            # Get the ROI for the left cheek
            self.get_roi(
                landmarks, 
                range(31, 32),
                roi_side, 
                0,
                -cheek_hor_translation,
                batch_id
            )

            # Get the ROI for the right cheek
            self.get_roi(
                landmarks, 
                range(35, 36),
                roi_side,
                0,
                cheek_hor_translation,
                batch_id
            )
            break


class ProcessVideo(Process):
    def __init__(self, filename, preprocess_analysis):
        Process.__init__(self, preprocess_analysis)
        self.video = cv2.VideoCapture(filename) 
        self.base_dest_dir = filename.strip(".mp4")
        if preprocess_analysis == "MD":
            if not self.base_dest_dir.endswith("_matrix_decomposition"):
                self.base_dest_dir = self.base_dest_dir + "_matrix_decomposition"

    def release(self):
        self.video.release()
        cv2.destroyAllWindows() 

    def get_frame(self):
        ret, frame = self.video.read() 
        return frame

    def save_data(self, database, batch_id, cursor=None, cnxn=None):
        batch_id_str = "".join(["B", format(batch_id, "05")])
        if database:
            # Insert data into the database
            for i in range(len(self.rois)):
                red_data=str(self.rois[i]["red_data"])
                green_data=str(self.rois[i]["green_data"])
                blue_data=str(self.rois[i]["blue_data"])
                collection_time=self.rois[i]["collection_time"]
                location_id=self.rois[i]["location_id"]
                # TODO: Add the device ID here so we can link the ROI data to the patient
                cursor.execute("INSERT INTO dbo.pulse_tracer_roi(location_id,collection_time,batch_id,blue_data,green_data,red_data,device_id,hr_analyzed,rr_analyzed,analysis_in_progress,preprocessing_analysis) VALUES (?,?,?,?,?,?,?,?,?,?,?)", (location_id,collection_time,batch_id,blue_data,green_data,red_data,self.device,False,False,False,self.preprocess_analysis))
            cnxn.commit()
            # TODO: FIX THIS
            return None, None
        else:
            # Add batch ID to destination filename
            # Check if the base directory exists
            if not os.path.exists(self.base_dest_dir):
                os.makedirs(self.base_dest_dir)
            '''
            # TODO: REMOVE
            roi_location = ROI_NUM_TO_WORD_MAP[str(self.rois[0]["location_id"])]
            '''
            filename = self.base_dest_dir.split("/")[-1]
            filename = "_".join([filename, batch_id_str])
            # filename = "_".join([filename, batch_id_str, roi_location])
            dest_file = os.path.join(self.base_dest_dir, filename)
            with open(f"{dest_file}.json", "w") as write_filename:
                json.dump(self.rois, write_filename)

            return dest_file, filename + ".json"
