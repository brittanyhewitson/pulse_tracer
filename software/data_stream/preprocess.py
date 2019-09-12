import os
import cv2
import sys
import pytz
import json
import click
import timeit
import logging

from datetime import datetime

from process_images import ProcessVideo
from dbclient.spectrum_metrics import SpectrumApi, NotFoundError

#spectrum_api = SpectrumApi()

# Set up logging
LOGGING_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(
    format=LOGGING_FORMAT, 
    stream=sys.stderr, 
    level=logging.INFO
)

TIMEZONE = pytz.timezone("Canada/Pacific")

LOCATION_ID_CHOICES = [
        "right_cheek",
        "left_cheek",
        "upper_nose",
        "mid_upper_nose",
        "mid_lower_nose",
        "lower_nose",
        "left_outer_brow",
        "left_mid_outer_brow",
        "left_mid_brow",
        "left_mid_inner_brow",
        "left_inner_brow",
        "right_inner_brow",
        "right_mid_inner_brow",
        "right_mid_brow",
        "right_mid_outer_brow",
        "right_outer_brow",
    ]

ROI_MAP = {
    "right_cheek": "31",
    "left_cheek": "35",
    "upper_nose": "27",
    "mid_upper_nose": "28",
    "mid_lower_nose": "29",
    "lower_nose": "30",
    "left_outer_brow": "17",
    "left_mid_outer_brow": "18",
    "left_mid_brow": "19",
    "left_mid_inner_brow": "20",
    "left_inner_brow": "21",
    "right_inner_brow": "22",
    "right_mid_inner_brow": "23",
    "right_mid_brow": "24",
    "right_mid_outer_brow": "25",
    "right_outer_brow": "26",
}


def get_video_roi_data(filename, roi_locations):
    """
    Processes a video to extract ROI at each frame in the clip

    Args:
        filename:   (str) full path to the video
    Returns:
        process_video.rois: (list) a list of dicts holding landmark info,
                            the time of the frame, and the ROI data
    """
    process_video = ProcessVideo(filename)
    current_datetime = datetime.now(TIMEZONE)
    process_video.batch_id = current_datetime.strftime("%Y%m%d%H%M%S")

    # Time the algorithm
    start = timeit.default_timer()
    while(True):
        # Read the video
        ret, frame = process_video.video.read()
        if frame is None:
            break

        # Add frame info to the class
        process_video.frame = frame
        process_video.gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        process_video.frame_time = datetime.now(TIMEZONE).isoformat()

        # Detect the face
        faces = process_video.detect_faces()
        if len(faces) == 0:
            continue

        # Need to add function for comparing multiple detected faces here

        # Get the landmarks
        process_video.get_landmarks(faces, roi_locations)

        # Show the image
        cv2.imshow('frame', process_video.frame)

        # Break if the "q" key is selected
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    # Log how long the algorithm took
    stop = timeit.default_timer()
    total_time = stop - start
    logging.info("Total time was %s" % total_time)
    
    # When everything done, release the capture
    process_video.video.release()
    cv2.destroyAllWindows()

    # Save roi as json 
    dest_file = filename.strip(".mp4") 
    with open(f"{dest_file}.json", "w") as filename:
        json.dump(process_video.rois, filename)

    return process_video.rois


@click.group()
def input_type():
    pass

@input_type.command()
@click.argument("filename", nargs=1)
@click.argument("roi_locations", nargs=-1)
def file(**kwargs):
    """
    For testing purposes only -- run the pipeline on an input video

    Args:
        filename:   (str) filepath to the mp4 to be analyzed
    """
    # Get the device metadata
    serial_number = os.environ.get("DEVICE_SERIAL_NUMBER")
    device_model = os.environ.get("DEVICE_MODEL")

    # Will not happen in production
    if serial_number is None or device_model is None:
        raise Exception("Please ensure the device has a serial number and model")

    # Get the device object from the database
    device = spectrum_api.get_or_create(
        "devices", 
        device_model=device_model,
        serial_number=serial_number,
    )

    # Get the patient associated with this device in the database
    try:
        patient = spectrum_api.get(
            "patients",
            device__id=device["id"]
        )
    except NotFoundError:
        id = device["id"]
        raise Exception(f"Please register the patient associated with device {id} on the database")
    
    # Pass this device and patient info to the preprocess function
    kwargs["device"] = device

    # Pass the ROI info
    roi_locations = []
    for roi_location in kwargs["roi_locations"]:
        try:
            roi_locations.append(int(ROI_MAP[roi_location]))
        except KeyError:
            logging.warning(f"Unrecognized ROI location {roi_location}. Skipping this ROI")
    
    if not roi_locations:
        raise Exception("No valid ROI locations provided")

    kwargs["roi_locations"] = roi_locations

    # Preprocess the data
    run_preprocess(**kwargs)


@input_type.command()
def stream(roi_locations):
    """
    Process images from a live stream
    """
    # starts capturing image from the default camera
    process_live = cv2.VideoCapture(0)
    while True:
        frame, ret = process_live.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        cv2.imshow('frame', frame)
        cv2.imshow('gray_frame', gray)
    
    #process_video = ProcessVideo(filename)
    current_datetime = datetime.now(TIMEZONE)
    process_live.batch_id = current_datetime.strftime("%Y%m%d%H%M%S")
    
    # Time the algorithm
    start = timeit.default_timer()
    # Capturing frames in an infinite loop
    while(True):
        # Read live camera
        ret, frame = process_live.read()
        if frame is None:
            break
    
        # Add frame info to the class
        process_live.frame = frame

        #Convert the captured video into a gray-scale
        process_live.gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        process_live.frame_time = datetime.now(TIMEZONE).isoformat()
        
        # Detect the face
        faces = process_live.detect_faces()
        if len(faces) == 0:
            continue

    # Need to add function for comparing multiple detected faces here

    # Get the landmarks
    process_live.get_landmarks(faces, roi_locations)

    # Show the image
    cv2.imshow('frame', process_live.frame)
    
    # Break if the "q" key is selected
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

    # Log how long the algorithm took
    stop = timeit.default_timer()
    total_time = stop - start
    logging.info("Total time was %s" % total_time)

    # When everything done, release the capture
    process_live.release()
    cv2.destroyAllWindows()

    # Save roi as json
    dest_file = filename.strip(".mp4")
    with open(f"{dest_file}.json", "w") as filename:
        json.dump(process_live.rois, filename)

    return process_live.rois

def run_preprocess(**kwargs):
    """
    Processes the data and then transmits to the VM for analysis

    Args:
        kwargs: (dict) contains filename, which is the full path to the
                video file
    """
    # Image Processing
    data = get_video_roi_data(kwargs["filename"], kwargs["roi_locations"])
    
    # Add the data to the database
    '''
    for roi in data:
        new_roi = spectrum_api.get_or_create(
            "rois",
            device=kwargs["device"]["id"],
            location_id=roi["location_id"],
            red_data=str(roi["red_data"]),
            green_data=str(roi["green_data"]),
            blue_data=str(roi["blue_data"]),
            collection_time=roi["collection_time"],
            batch_id=roi["batch_id"]
        )
    '''


if __name__=='__main__':
    input_type()
