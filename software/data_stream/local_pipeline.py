import os
import re
import sys
import click
import subprocess
import logging
import time

from datetime import datetime
#from pynput.keyboard import Key, Listener

from templates import PI_IP

from helpers import (
    connect_to_client,
    run_video_preprocess,
    run_analysis_pipeline,
)
from templates import (
    LOGGING_FORMAT,
    TIMEZONE,
    PREPROCESS_CHOICES
)

# Set up logging
logging.basicConfig(format=LOGGING_FORMAT, stream=sys.stderr, level=logging.INFO)


@click.group()
def input_type():
    """
    Run the preprocessing pipeline on a local machine by either remotely connecting to the Raspberry 
    Pi to launch data collection and send data back to local for analysis, or by running on a video 
    that already exists on the local machine. ROI data is then transferred either to the remote database
    or a local database for downstream analysis. 
    """
    pass


@input_type.command()
# TODO: Add database
@click.argument("roi_locations", nargs=-1)
@click.option("--input_file", help="The full path to the input file to run the analysis pipeline on")
@click.option("--preprocess_analysis", default="MD", type=click.Choice(PREPROCESS_CHOICES), help="The preprocessing algorithm used for the downstream analysis")
def local_video(**kwargs):
    """
    Run analysis pipeline on video existing on local machine
    """
    output_dir = run_video_preprocess(
        video_file=input_video,
        roi_locations=kwargs["roi_locations"],
        preprocess_analysis=kwargs["preprocess_analysis"],
        database=False
    )

    run_analysis_pipeline(
        preprocess_analysis=kwargs["preprocess_analysis"],
        json_filepath=output_dir,
    )


@input_type.command()
# TODO: Add database flag
@click.argument("roi_locations", nargs=-1)
@click.option("--preprocess_analysis", default="MD", type=click.Choice(PREPROCESS_CHOICES), help="The preprocessing algorithm used for the downstream analysis")
@click.option("--output_filename", help="The name for the generated JSON files")
@click.option("--destination_filepath", help="Full path to write the output JSON files on the local machine")
@click.option("--database", is_flag=True)
@click.option("--video_length", default="30", help="Length of the video to record on the Raspberry Pi")
def remote_video(**kwargs):
    """
    Remotely access the Raspberry Pi to record a video

    ARGS:
        roi_locations:
        preprocess_analysis:
        output_filename:
        destination_filepath:
        video_length:
    """
    # SSH into the Raspberry Pi
    logging.info("Conneting to the Raspberry Pi")
    ssh_client = connect_to_client()

    # Check the inputs
    if kwargs["output_filename"] is None:
        # TODO: Add nice error classes instead of raising exceptions
        raise Exception("Missing an output filename")
    if kwargs["destination_filepath"] is None and not kwargs["database"]:
        raise Exception("Missing the filepath to the data destination on local machine")

    # Add "matrix_decomposition" to the end of the file if necessary
    if kwargs["preprocess_analysis"] == "MD":
        kwargs["output_filename"] = "_".join([kwargs["output_filename"], "matrix_decomposition"])
    
    if kwargs["database"]:
        database = True
    else:
        database = False

    # Create the name of the remote output location
    remote_output_file = os.path.join(
        "/home/pi/Desktop",
        kwargs["output_filename"] + ".h264"
    )
    
    # TODO: Check if the file already exists and delete it if it does

    # Record the video on the pi
    video_length = int(kwargs["video_length"])
    cmd = f"python3 /home/pi/Desktop/capstone/software/data_stream/rpi_camera_collect.py {remote_output_file} --video_length {video_length}"
    logging.info("Launching remote data collection on Raspberry Pi")
    stdin, stdout, stderr = ssh_client.exec_command(cmd)
    exit_status = stdout.channel.recv_exit_status() 

    # Check the command exited successfully
    if exit_status != 0:
        logging.error(stderr.read())
        # TODO: Nice error class here
        raise Exception()
    
    # Remotely run preprocess on the data collected by the Raspberry Pi
    output_dir, batch_ids = run_video_preprocess(
        video_file=remote_output_file, 
        roi_locations=kwargs["roi_locations"],
        preprocess_analysis=kwargs["preprocess_analysis"],
        ssh_client=ssh_client,
        database=database,
    )

    if not kwargs["database"]:
        base_local_output_filepath = kwargs["destination_filepath"]
        local_output_filepath = os.path.join(
            kwargs["destination_filepath"], 
            kwargs["output_filename"]
        )
        # TODO: Check if output file already exists on local and delete if it does
        logging.info("Copying video file to local machine")
        # Make the local directory
        if not os.path.exists(base_local_output_filepath):
            os.makedirs(base_local_output_filepath)

        # Rsync the file from the Raspberry Pi to the local
        cmd = f"rsync -avPL pi@{PI_IP}:{output_dir} {base_local_output_filepath}"
        subprocess.check_call(cmd, shell=True)
        # TODO: Check the files were copied correctly (checksum/filesize) before closing the SSH client
        ssh_client.close()
    else:
        local_output_filepath = None

    # Run the analysis pipeline
    # TODO: Batch ID not required here? change in run_pipeline.py
    run_analysis_pipeline(
        preprocess_analysis=kwargs["preprocess_analysis"],
        json_filepath=local_output_filepath,
    )
    

@input_type.command()
@click.argument("destination_filepath")
@click.argument("roi_locations", nargs=-1)
@click.option("--database", is_flag=True)
@click.option("--preprocess_analysis", default="MD", type=click.Choice(PREPROCESS_CHOICES), help="The preprocessing algorithm used for the downstream analysis")
@click.option("--video_length", default=30, help="Length of the video segments for processing")
def remote_stream(**kwargs):
    """
    Remotely access the Raspberry Pi to stream the camera

    ARGS:
        roi_locations:
        preprocess_analysis:
        output_filename:
        destination_filepath:
    """
    # SSH into the Raspberry Pi
    logging.info("Conneting to the Raspberry Pi")
    ssh_client = connect_to_client()
    sftp_client = ssh_client.open_sftp()

    if not os.path.exists(kwargs["destination_filepath"]):
        os.makedirs(kwargs["destination_filepath"])

    # Create arguments for the command 
    destination_filepath = kwargs["destination_filepath"]
    video_length = kwargs["video_length"]
    preprocess_analysis = kwargs["preprocess_analysis"]

    # Launch script to check for data in the output
    cmd = f"python3 check_local_files.py {destination_filepath}"
    for roi in kwargs["roi_locations"]:
        cmd += f" {roi}"
    if kwargs["database"]:
        cmd += " --database"
    cmd += f" --preprocess_analysis {preprocess_analysis}"
    proc = subprocess.Popen(cmd, shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)

    # Copy data from the Raspberry Pi to the local machine
    while True:
        current_datetime = datetime.now(TIMEZONE)
        batch_id = current_datetime.strftime("%Y%m%d%H%M%S")
        pi_data_dir = os.path.join("/home/pi/Desktop", current_datetime.strftime("%Y_%m_%d"))
        local_filepath = os.path.join(kwargs["destination_filepath"], batch_id + ".h264")

        # Make the data directory if it doesn't already exist
        try:
            sftp_client.stat(pi_data_dir)
        except IOError:
            sftp_client.mkdir(pi_data_dir)

        pi_filepath = os.path.join(pi_data_dir, batch_id + ".h264")
        cmd = f"source /home/pi/.bash_profile; source /home/pi/envs/pulse_tracer/bin/activate; python3 /home/pi/Desktop/capstone/software/data_stream/rpi_camera_collect.py {pi_filepath} --video_length {video_length}"
        
        logging.info(f"Starting data collection on Raspberry Pi for {video_length} seconds")
        stdin, stdout, stderr = ssh_client.exec_command(cmd)
        exit_status = stdout.channel.recv_exit_status() 

        # If the remote facial detection was successful, read the output directory
        if exit_status == 0:
            # Transfer data from Raspberry Pi to local
            logging.info("Copying remote file to local machine")
            sftp_client.get(pi_filepath, local_filepath + ".partial")
            os.rename(local_filepath + ".partial", local_filepath)
        else:
            logging.error(stderr.read())
            raise Exception()
    
    sftp_client.close()
    ssh_client.close()          


if __name__=='__main__':
    input_type()