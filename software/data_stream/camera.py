import os
import json
import numpy as np

from datetime import datetime
from picamera import PiCamera
from picamera.array import PiRGBArray
from time import sleep

from templates import TIMEZONE
from data_stream.process_images import Process


class Camera(object):
    """
    Python application that access the PiCamera, capture an image from the stream
    """
    #Accessing the camera and capture an image
    def __init__(self):
        self.cam = PiCamera()
        self.cam.resolution = (640, 480)
        self.cam.framerate = 30
        self.rawCapture = PiRGBArray(self.cam)
        self.cam.capture(self.rawCapture, format="bgr") 
        self.valid = True
        self.rawCapture.truncate(0)
        
     
    #Return a frame from the camera
    def get_frame(self):
       if self.valid:
            for frame in self.cam.capture_continuous(self.rawCapture, format="bgr"):
                image=frame.array
                self.rawCapture.truncate(0)
                return image
       else:
           frame = np.ones((480,640,3), dtype=np.uint8)
           col = (0,256,256)
       return image

    def release(self):
        self.cam.stop_preview()


class ProcessStream(Process):
    def __init__(self, preprocess_analysis, data_dir):
        Process.__init__(self, preprocess_analysis)
        self.cameras = []
        self.selected_cam = 0
        self.camera = Camera()
        self.cameras.append(self.camera)
        current_datetime = datetime.now(TIMEZONE)
        self.output_filename = current_datetime.strftime("%Y%m%d%H%M%S")
        if preprocess_analysis == "MD":
            self.output_filename = self.output_filename + "_matrix_decomp"
        self.data_dir = os.path.join(data_dir, self.output_filename)

    def release(self):
        self.cameras[self.selected_cam].release()

    def get_frame(self):
        return self.cameras[self.selected_cam].get_frame()

    def collect_video(self, output_filename, video_length):
        self.camera.cam.start_preview()
        self.camera.cam.start_recording(output_filename)
        sleep(video_length)
        self.camera.cam.stop_recording()
        self.camera.cam.stop_preview()

    def save_data(self, database, batch_id, cursor=None, cnxn=None):
        batch_id_str = "".join(["B", format(batch_id, "05")])
        if database:
            # TODO: Add database stuff here
            if database:
                # Insert data into the database
                for i in range(len(self.rois)):
                    red_data=str(self.rois[i]["red_data"])
                    green_data=str(self.rois[i]["green_data"])
                    blue_data=str(self.rois[i]["blue_data"])
                    collection_time=self.rois[i]["collection_time"]
                    batch_id=self.rois[i]["batch"]
                    location_id=self.rois[i]["location_id"]
                    # TODO: Add the device ID here so we can link the ROI data to the patient
                    cursor.execute("INSERT INTO dbo.pulse_tracer_roi(location_id,collection_time,batch_id,blue_data,green_data,red_data,device_id,hr_analyzed,rr_analyzed,analysis_in_progress,preprocessing_analysis) VALUES (?,?,?,?,?,?,?,?,?,?,?)", (location_id,collection_time,batch_id,blue_data,green_data,red_data,self.device,False,False,False,self.preprocess_analysis))
                cnxn.commit()
                # TODO: FIX THIS
                return None, None
        else:
            # Check if the base directory exists
            if not os.path.exists(self.data_dir):
                os.makedirs(self.data_dir)
            # Add batch ID to destination filename
            filename = "_".join([self.output_filename, batch_id_str])
            dest_file = os.path.join(self.data_dir, filename)
            with open(f"{dest_file}.json", "w") as write_filename:
                json.dump(self.rois, write_filename)

            return dest_file, filename + ".json"

