import os
import re
import sys
import click
import subprocess
import logging
import paramiko
import time

from data_stream.preprocess import video_stream_cmd, video_file_cmd
from analysis.run_pipeline import matrix_decomposition_cmd, fd_bss_cmd
from templates import (
    LOGGING_FORMAT,
    TIMEZONE,
    PI_IP,
    PREPROCESS_CHOICES
)

# Set up logging
logging.basicConfig(format=LOGGING_FORMAT, stream=sys.stderr, level=logging.INFO)


def connect_to_client():
    """
    """
    # Connect to the client
    ssh_client = paramiko.SSHClient()
    ssh_client.load_system_host_keys()
    ssh_client.connect(PI_IP, username="pi")
    return ssh_client

def run_video_preprocess(video_file, roi_locations, preprocess_analysis, ssh_client=None):
    """
    Runs the whole pipeline when supplying a video file
    """
    # Check if the JSON file already exists
    logging.info("Running preprocess to determine ROI")

    # Run the Preprocessing algorithm to get ROIs
    if ssh_client:
        cmd = f"source /home/pi/.bash_profile; source /home/pi/envs/pulse_tracer/bin/activate; python3 /home/pi/Desktop/capstone/software/data_stream/preprocess.py video-file {video_file}"
        for roi_location in roi_locations:
            cmd += f" {roi_location}"
        if preprocess_analysis == "matrix_decomposition":
            cmd += f" --matrix_decomposition"
        stdin, stdout, stderr = ssh_client.exec_command(cmd)
        exit_status = stdout.channel.recv_exit_status() 

        # If the remote facial detection was successful, read the output directory
        if exit_status == 0:
            output_dir = stdout.read().decode("utf-8").strip("\n")
            '''
            output_dir_regex = r"b\'([/\w]+)"
            if re.match(output_dir_regex, output_dir, re.I):
                output_dir = re.match(output_dir_regex, output_dir, re.I).group(1)
            '''
        # Otherwise log the error
        else:
            logging.error(stderr.read())
            raise Exception()
    else:
        if preprocess_analysis == "matrix_decomposition":
            matrix_decomposition = True
        else:
            matrix_decomposition = False
        output_dir = video_file_cmd(
            filename=video_file,
            roi_locations=roi_locations,
            matrix_decomposition=matrix_decomposition,
            database=False
        )

    # Check that the JSON output was successfully created
    return output_dir


def run_analysis_pipeline(preprocess_analysis, json_filepath, database=False):
    if preprocess_analysis == "fd_bss":
        fd_bss_cmd(
            json_filepath=json_filepath,
            batch_id="batch_id",
            database=database
        )
    else:
        matrix_decomposition_cmd(
            json_filepath=json_filepath,
            batch_id="batch_id",
            database=database
        )


@click.group()
def input_type():
    pass


@input_type.command()
@click.argument("roi_locations", nargs=-1)
@click.option("--input_file", help="The full path to the input file to run the analysis pipeline on")
@click.option("--preprocess_analysis", default="fd_bss", type=click.Choice(PREPROCESS_CHOICES), help="The preprocessing algorithm used for the downstream analysis")
def local_video(**kwargs):
    """
    Run analysis pipeline on video existing on local machine
    """
    output_dir = run_video_preprocess(
        video_file=kwargs["input_file"],
        roi_locations=kwargs["roi_locations"],
        preprocess_analysis=kwargs["preprocess_analysis"]
    )

    run_analysis_pipeline(
        preprocess_analysis=kwargs["preprocess_analysis"],
        json_filepath=output_dir,
    )


@input_type.command()
@click.argument("roi_locations", nargs=-1)
@click.option("--preprocess_analysis", default="fd_bss", type=click.Choice(PREPROCESS_CHOICES), help="The preprocessing algorithm used for the downstream analysis")
@click.option("--output_filename", help="The name for the generated JSON files")
@click.option("--destination_filepath", help="Full path to write the output JSON files on the local machine")
@click.option("--video_length", default="30", help="Length of the video to record on the Raspberry Pi")
def remote_video(**kwargs):
    """
    Remotely access the Raspberry Pi to record a video
    """
    # SSH into the Raspberry Pi
    logging.info("Conneting to the Raspberry Pi")
    ssh_client = connect_to_client()

    # Check the inputs
    if kwargs["output_filename"] is None:
        # TODO: Add nice error classes instead of raising exceptions
        raise Exception("Missing an output filename")
    if kwargs["destination_filepath"] is None:
        raise Exception("Missing the filepath to the data destination on local machine")

    # Add "matrix_decomposition" to the end of the file if necessary
    if kwargs["preprocess_analysis"] == "matrix_decomposition":
        kwargs["output_filename"] = "_".join([kwargs["output_filename"], "matrix_decomposition"])

    # Create the name of the remote output location
    remote_output_file = os.path.join(
        "/home/pi/Desktop",
        kwargs["output_filename"] + ".h264"
    )
    base_local_output_filepath = kwargs["destination_filepath"]
    local_output_filepath = os.path.join(
        kwargs["destination_filepath"], 
        kwargs["output_filename"]
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

    # Remotely run preprocess on the data collected on the Raspberry Pi
    output_dir = run_video_preprocess(
        video_file=remote_output_file, 
        roi_locations=kwargs["roi_locations"],
        preprocess_analysis=kwargs["preprocess_analysis"],
        ssh_client=ssh_client
    )

    # TODO: Check if output file already exists on local and delete if it does
    logging.info("Copying video file to local machine")
    # Make the local directory
    if not os.path.exists(base_local_output_filepath):
        os.makedirs(base_local_output_filepath)

    # Rsycn the file from the Raspberry Pi to the local
    cmd = f"rsync -avPL pi@{PI_IP}:{output_dir} {base_local_output_filepath}"
    subprocess.check_call(cmd, shell=True)
    # TODO: Check the files were copied correctly before closing the SSH client
    ssh_client.close()

    # Run the analysis pipeline
    # TODO: Batch ID not required here? change in run_pipeline.py
    run_analysis_pipeline(
        preprocess_analysis=kwargs["preprocess_analysis"],
        json_filepath=local_output_filepath,
    )
    

@input_type.command()
@click.argument("roi_locations", nargs=-1)
@click.option("--preprocess_analysis", default="fd_bss", type=click.Choice(PREPROCESS_CHOICES), help="The preprocessing algorithm used for the downstream analysis")
@click.option("--output_filename", help="The name for the generated JSON files")
@click.option("--destination_filepath", help="Full path to write the output JSON files on the local machine")
def remote_stream():
    """
    Remotely access the Raspberry Pi to stream the camera
    """
    # SSH into the Raspberry Pi
    logging.info("Conneting to the Raspberry Pi")
    ssh_client = connect_to_client()

    ssh_client.close()




if __name__=='__main__':
    input_type()