import os
import cv2
import sys 
import click
import timeit
import logging
import subprocess
import pyodbc
import numpy as np

from datetime import datetime
from data_stream.process_images import ProcessVideo
from templates import (
    LOGGING_FORMAT,
    TIMEZONE,
    LOCATION_ID_CHOICES,
    ROI_WORD_TO_NUM_MAP,
    PREPROCESS_CHOICES
)

from dbclient.spectrum_metrics import SpectrumApi, NotFoundError
# Set up logging
logging.basicConfig(
    format=LOGGING_FORMAT, 
    stream=sys.stderr, 
    level=logging.INFO
)

spectrum_api = SpectrumApi() 


def rpi_server_config():
    """
    Configure the server so data can be sent to the Azure cloud database
    """
    dsn = 'rpitestsqlserverdatasource'
    user = os.environ.get('AZURE_DB_USER')
    database = os.environ.get('AZURE_DB', 'spectrum_metrics')
    username = os.environ.get('AZURE_DB_USERNAME')
    password = os.environ.get('AZURE_DB_PASSWORD')
    connString = 'DSN={0};UID={1};PWD={2};DATABASE={3};'.format(dsn,user,password,database)
    cnxn = pyodbc.connect(connString)
    return cnxn


def local_server_config():
    server = 'tcp:'  + os.environ.get('AZURE_SERVER', 'capstonesfu.database.windows.net')
    database = os.environ.get('AZURE_DB', 'spectrum_metrics')
    username = os.environ.get('AZURE_DB_USERNAME')
    password = os.environ.get('AZURE_DB_PASSWORD')
    cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
    return cnxn


def send_batch(process_video, database, batch_id, cursor, cnxn, transfer, batch_ids, remote_output_dir, remote_host):
    # Initialize batch ID
    if database:
        batch_id = spectrum_api.create(
                'batches',
                preprocessing_analysis=process_video.preprocess_analysis,
                creation_time=datetime.now(TIMEZONE).isoformat(),
                device=process_video.device
            )["id"]
    else:
        batch_id += 1
    # Store JSON data on local machine
    dest_filepath, dest_filename = process_video.save_data(
                                        database,
                                        batch_id,
                                        cursor,
                                        cnxn,
                                    )
    if transfer:
        remote_dest_file = os.path.join(remote_output_dir, dest_filename)
        cmd = f"rsync -avPL {dest_filepath} {remote_host}:{remote_dest_file}"
        subprocess.check_call(cmd, shell=True)
    process_video.rois = []
    batch_ids.append(batch_id)
    '''
    # Update the batch ID
    if database:
        batch_id = spectrum_api.create(
            'batches',
            preprocessing_analysis=process_video.preprocess_analysis,
            creation_time=datetime.now(TIMEZONE).isoformat(),
            device=process_video.device
        )["id"]
    else:
        batch_id += 1
    '''
        
    return batch_id, batch_ids


def get_roi_data(process_video, **kwargs):
    """
    Processes a video to extract ROIs for each frame
    """
    batch_id = 0
    batch_ids = []
    transfer = False
    cnxn = None
    cursor = None
    remote_host = None
    remote_output_dir = None

    try:
        if kwargs["remote_host"] and kwargs["remote_output_dir"]:
            remote_host = kwargs["remote_host"]
            remote_output_dir = kwargs["remote_output_dir"]
            transfer = True
    except KeyError:
        pass

    #Create connection to the SQL Server
    if kwargs["database"] == True:
        if os.environ.get("IS_RPI") == "True":
            cnxn = rpi_server_config()
        else:
            cnxn = local_server_config()
        cursor = cnxn.cursor()

    # Time the algorithm
    start = timeit.default_timer()
    num_frames = 0
    while(True):
        frame = process_video.get_frame()
        if frame is None:
            if num_frames > 600:
                batch_id, batch_ids = send_batch(process_video, kwargs["database"], batch_id, cursor, cnxn, transfer, batch_ids, remote_output_dir, remote_host)
            break

        # Add frame info to the class
        process_video.frame = frame
        process_video.gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        process_video.frame_time = datetime.now(TIMEZONE).isoformat()

        # Detect the face
        faces = process_video.detect_faces()
        if not faces:
            continue

        # TODO: Need to add function for comparing multiple detected faces here

        # Get the landmarks
        process_video.get_landmarks(faces, kwargs["roi_locations"], batch_id)

        # Show the image
        # cv2.imshow('frame', process_video.frame)

        # Save the data
        # TODO: Add counter here to count number of frames. Once it reaches
        # 900 (30 seconds of video) increment the counter 
        if num_frames == 900:
            batch_id, batch_ids = send_batch(process_video, kwargs["database"], batch_id, cursor, cnxn, transfer, batch_ids, remote_output_dir, remote_host)
            num_frames = 0
        num_frames += 1

        # Break if the "q" key is selected
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    # Log how long the algorithm took
    stop = timeit.default_timer()
    total_time = stop - start
    logging.info(f"Total time was {total_time}")
    
    # When everything is done, release the capture
    process_video.release()

    return process_video.rois, batch_ids

def run_preprocess(process_video, **kwargs):
    """
    For both stream and video
    """
    #spectrum_api = SpectrumApi()
    # Get the local device metadata
    serial_number = os.environ.get("DEVICE_SERIAL_NUMBER")
    device_model = os.environ.get("DEVICE_MODEL")

    # Ensure the metadata is not None
    if serial_number is None or device_model is None:
        raise Exception("Please ensure the device has a serial number and model")
    
    # Get the device object from the database
    device = spectrum_api.get_or_create(
        "devices", 
        device_model=device_model,
        serial_number=serial_number,
    )
    device_id = device["id"]

    # Get the patient associated with this device in the database
    try:
        patient = spectrum_api.get(
            "patients",
            device__id=device["id"]
        )
        
    except NotFoundError:
        raise Exception(f"Please register the patient associated with device {id} on the database")
    
    # Pass this device and patient info to the preprocess function
    process_video.device = device_id

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

    roi_data, batch_ids = get_roi_data(process_video, **kwargs)

    return roi_data, batch_ids


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
@click.option("--preprocess_analysis", default="matrix_decomposition", type=click.Choice(PREPROCESS_CHOICES))
@click.option("--database", is_flag=True)
def video_file(**kwargs):
    output_dir, batch_ids = video_file_cmd(**kwargs)


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
        kwargs["filename"] = mp4_file

    elif filename.endswith(".mp4"):
        logging.info("MP4 file already exists")
    else:
        raise Exception("Unrecognized file format")

    # Create the process object
    process_video = ProcessVideo(
        filename=kwargs["filename"],
        preprocess_analysis=kwargs["preprocess_analysis"]
    )
    roi_data, batch_ids = run_preprocess(process_video, **kwargs)

    # Print to console for local_pipeline output
    print(process_video.base_dest_dir)
    return process_video.base_dest_dir, batch_ids


@video_type.command()
@click.argument("roi_locations", nargs=-1)
@click.option("--preprocess_analysis", default="matrix_decomposition", type=click.Choice(PREPROCESS_CHOICES))
@click.option("--database", is_flag=True)
@click.option("--data_dir", required=False, default=os.getcwd())
@click.option("--remote_output_dir")
@click.option("--remote_host")
def video_stream(**kwargs):
    output_dir, batch_ids = video_stream_cmd(**kwargs)


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
        preprocess_analysis=kwargs["preprocess_analysis"],
        data_dir=kwargs["data_dir"]
    )
    
    roi_data, batch_ids = run_preprocess(process_video, **kwargs)
    
    return process_video.data_dir, batch_ids


if __name__=='__main__':
    video_type()