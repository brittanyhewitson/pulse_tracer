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

spectrum_api = SpectrumApi()

# Set up logging
LOGGING_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(
    format=LOGGING_FORMAT, 
    stream=sys.stderr, 
    level=logging.INFO
)

TIMEZONE = pytz.timezone("Canada/Pacific")


def get_video_roi_data(filename):
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
        process_video.get_landmarks(faces)

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

    # Preprocess the data
    run_preprocess(**kwargs)


@input_type.command()
def stream():
    """
    Process images from a live stream
    """
    pass


def run_preprocess(**kwargs):
    """
    Processes the data and then transmits to the VM for analysis

    Args:
        kwargs: (dict) contains filename, which is the full path to the
                video file
    """
    # Image Processing
    data = get_video_roi_data(kwargs["filename"])

    '''
    # Add the data to the database
    for roi in data:
        new_roi = spectrum_api.get_or_create(
            "rois",
            device=kwargs["device"]["id"],
            location_id=roi["location_id"],
            red_data=roi["red_data"],
            green_data=roi["green_data"],
            blue_data=roi["blue_data"],
            collection_time=roi["collection_time"],
            batch_id=roi["batch_id"]
        )
    '''

    
    # Data Transmission


if __name__=='__main__':
    input_type()
