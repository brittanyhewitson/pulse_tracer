import os
import cv2
import sys 
import click
import timeit
import logging
import datetime
import subprocess

import numpy as np

from datetime import datetime
from process_images import ProcessVideo
from templates import (
    LOGGING_FORMAT,
    TIMEZONE,
    LOCATION_ID_CHOICES,
    ROI_WORD_TO_NUM_MAP
)


# Set up logging
logging.basicConfig(
    format=LOGGING_FORMAT, 
    stream=sys.stderr, 
    level=logging.INFO
)


def get_roi_data(process_video, **kwargs):
    """
    Processes a video to extract ROIs for each frame
    """
    # TODO: Need something else for the batch ID here
    #current_datetime = datetime.now(TIMEZONE)
    #process_video.batch_id = current_datetime.strftime("%Y%m%d%H%M%S")
    batch_id = 0
    transfer = False

    try:
        if kwargs["remote_user"] and kwargs["remote_output_dir"] and kwargs["remote_ip"]:
            user = kwargs["remote_user"]
            remote_output_dir = kwargs["remote_output_dir"]
            ip = kwargs["remote_ip"]
            transfer = True
    except KeyError:
        pass

    # Time the algorithm
    start = timeit.default_timer()
    num_frames = 0
    while(True):
        frame = process_video.get_frame()
        if frame is None:
            break

        # Add frame info to the class
        process_video.frame = frame
        process_video.gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        process_video.frame_time = datetime.now(TIMEZONE).isoformat()

        # Detect the face
        faces = process_video.detect_faces()
        if not faces:
            continue

        # Need to add function for comparing multiple detected faces here

        # Get the landmarks
        process_video.get_landmarks(faces, kwargs["roi_locations"], batch_id)

        # Show the image
        cv2.imshow('frame', process_video.frame)

        # Save the data
        # TODO: Add counter here to count number of frames. Once it reaches
        # 900 (30 seconds of video) increment the counter 
        num_frames += 1
        if num_frames == 10:
            num_frames = 0
            dest_filepath, dest_filename = process_video.save_data(kwargs["database"], batch_id)
            if transfer:
                remote_dest_file = os.path.join(remote_output_dir, dest_filename)
                cmd = f"rsync -avPL {dest_filepath} {user}@{ip}:{remote_dest_file}"
                subprocess.check_call(cmd, shell=True)
            process_video.rois = []
            batch_id += 1

        # Break if the "q" key is selected
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    # Log how long the algorithm took
    stop = timeit.default_timer()
    total_time = stop - start
    logging.info(f"Total time was {total_time}")
    
    # When everything is done, release the capture
    process_video.release()

    return process_video.rois

def run_preprocess(process_video, **kwargs):
    """
    For both stream and video
    """
    # Get the local device metadata
    serial_number = os.environ.get("DEVICE_SERIAL_NUMBER")
    device_model = os.environ.get("DEVICE_MODEL")

    # Ensure the metadata is not None
    if serial_number is None or device_model is None:
        raise Exception("Please ensure the device has a serial number and model")

    '''
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
    '''
    # Check if ROI locations are valid
    if kwargs["roi_locations"][0] == "full_face":
        kwargs["roi_locations"] = LOCATION_ID_CHOICES[:-1]
    roi_locations = []
    for roi_location in kwargs["roi_locations"]:
        try:
            roi_locations.append(int(ROI_WORD_TO_NUM_MAP[roi_location]))
        except KeyError:
            logging.warning(f"Unrecognized ROI location {roi_location}. Skipping this ROI")
    
    # Check if there are any valid ROI locations
    if not roi_locations:
        raise Exception("No valid ROI locations provided")

    kwargs["roi_locations"] = roi_locations

    roi_data = get_roi_data(process_video, **kwargs)


@click.group()
def video_type():
    """
    Argument that specifies whether the analysis will be run on a saved video file
    or the live Raspberry Pi camera stream
    """
    pass


@video_type.command()
@click.argument("filename", nargs=1)
@click.argument("roi_locations", nargs=-1)
@click.option("--matrix_decomposition", is_flag=True)
@click.option("--database", is_flag=True)
def video_file(**kwargs):
    output_dir = video_file_cmd(**kwargs)


def video_file_cmd(**kwargs):
    """
    For testing and QA purposes only -- run the preprocessing pipeline
    on an input video. 
    
    Args:
        filename:               (str) filepath to the .h264 or .mp4 video file
        roi_locations:          (str) to specify which ROIs to select
        matrix_decomposition:   (bool) a flag for which preprocess analysis to use, and 
                                therefore how to save the ROI data
        database:               (bool) a flag for whether to save the data to the Azure database
                                or as a file on the local machine
    """
    # Check that the file exists
    if not os.path.exists(kwargs["filename"]):
        raise Exception("The supplied file does not exist")
    
    filename = kwargs["filename"]
    # If this is the raw data, convert to MP4
    if filename.endswith(".h264"):
        logging.info("Creating mp4 from h264")
        mp4_file = filename.strip(".h264") + ".mp4"
        cmd = f"MP4Box -fps 30 -add {filename} {mp4_file}"
        subprocess.check_call(cmd, shell=True)
    elif filename.endswith(".mp4"):
        logging.info("MP4 file already exists")
        mp4_file = filename
    else:
        raise Exception("Unrecognized file format")

    kwargs["filename"] = mp4_file

    process_video = ProcessVideo(
        filename=kwargs["filename"],
        matrix_decomposition=kwargs["matrix_decomposition"]
    )

    run_preprocess(process_video, **kwargs)

    # Print to consolde for local_pipeline output
    print(process_video.base_dest_dir)
    return process_video.base_dest_dir


@video_type.command()
@click.argument("roi_locations", nargs=-1)
@click.option("--matrix_decomposition", is_flag=True)
@click.option("--database", is_flag=True)
@click.option("--data_dir", required=False, default=os.getcwd())
@click.option("--remote_output_dir")
@click.option("--remote_ip")
@click.option("--remote_user")
def video_stream(**kwargs):
    output_dir = video_stream_cmd(**kwargs)


def video_stream_cmd(**kwargs):
    """
    For production and demo runs. Runs the preprocessing pipeline on the live stream feed 
    from the Raspberry Pi 

    Args:
        roi_locations:          (str) to specify which ROIs to select
        matrix_decomposition:   (bool) a flag for which preprocess analysis to use, and 
                                therefore how to save the ROI data
        database:               (bool) a flag for whether to save the data to the Azure database
                                or as a file on the local machine
    """
    from camera import ProcessStream
    process_video = ProcessStream(
        matrix_decomposition=kwargs["matrix_decomposition"],
        data_dir=kwargs["data_dir"]
    )

    run_preprocess(process_video, **kwargs)
    
    return process_video.data_dir


if __name__=='__main__':
    video_type()