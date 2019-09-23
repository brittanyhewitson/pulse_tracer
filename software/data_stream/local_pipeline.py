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


def video_run(video_file, roi_locations, preprocess_analysis, ssh_client=None):
    """
    Runs the whole pipeline when supplying a video file
    """
    # Check if the JSON file already exists
    logging.info("Running preprocess to determine ROI")

    # Run the Preprocessing algorithm to get ROIs
    if ssh_client:
        cmd = f"source /home/pi/.bash_profile; python3 /home/pi/Desktop/capstone/software/data_stream/preprocess.py video-file {video_file}"
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


@click.group()
def input_type():
    pass


@input_type.command()
@click.argument("roi_locations", nargs=-1)
@click.option("--stream", is_flag=True)
@click.option("--remote", is_flag=True)
@click.option("--filename", required=False)
@click.option("--destination_filepath", required=False)
@click.option("--preprocess_analysis", default="fd_bss", type=click.Choice(PREPROCESS_CHOICES))
def dev(**kwargs):
    """
    Runs pipeline without Azure VMs or use of database
    """
    if kwargs["remote"]:
        # SSH into the Raspberry Pi
        logging.info("Conneting to the Raspberry Pi")
        ssh_client = connect_to_client()
        
        if not kwargs["stream"]:
            # Check inputs
            if kwargs["filename"] is None:
                raise Exception("Missing an output filename")
            if kwargs["destination_filepath"] is None:
                raise Exception("Missing the filepath to the data destination")

            if kwargs["preprocess_analysis"] == "matrix_decomposition":
                kwargs["filename"] = "_".join([kwargs["filename"], "matrix_decomposition"])

            # Create the output locations
            remote_output_file = os.path.join(
                "/home/pi/Desktop", 
                kwargs["filename"] + ".h264"
            )
            base_local_output_filepath = kwargs["destination_filepath"]
            local_output_filepath = os.path.join(
                kwargs["destination_filepath"], 
                kwargs["filename"]
            )
            # TODO: Check if the file already exists and delete if it does

            # Record the video data
            video_length = 5
            cmd = f"python3 /home/pi/Desktop/capstone/software/data_stream/rpi_camera_collect.py {remote_output_file} --video_length {video_length}"
            logging.info("Launching remote data collection on Raspberry Pi")
            stdin, stdout, stderr = ssh_client.exec_command(cmd)
            time.sleep(video_length)

            # Run preprocess on the data and get the output directory where JSON data is stored
            output_dir = video_run(
                remote_output_file, 
                kwargs["roi_locations"], 
                kwargs["preprocess_analysis"],
                ssh_client=ssh_client
            )

            # TODO: Check if the file already exists and delete if it does

            logging.info("Copying video file to local")
            # Make the local directory if it doesn't exist yet
            if not os.path.exists(base_local_output_filepath):
                os.makedirs(base_local_output_filepath)

            # Rsync the file from remote to local
            cmd = f"rsync -avPL pi@{PI_IP}:{output_dir} {base_local_output_filepath}"
            subprocess.check_call(cmd, shell=True)
            ssh_client.close()

            # Run the analysis pipeline
            if kwargs["preprocess_analysis"] == "fd_bss":
                fd_bss_cmd(
                    json_filepath=local_output_filepath,
                    batch_id="batch_id",
                    database=False
                )
            else:
                matrix_decomposition_cmd(
                    json_filepath=local_output_filepath,
                    batch_id="batch_id",
                    database=False
                )
        # TODO: Add remote stream run (if possible....)

    else:
        if not kwargs["stream"]:
            output_file = os.path.join(
                "/home/pi/Desktop", 
                kwargs["filename"] + ".h264"
            )
            video_length = 30
            cmd = f"python3 rpi_camera_collect.py {output_file} --video_length {video_length}"
            logging.info("Launching local data collection")
            subprocess.check_call(cmd, shell=True)

            output_dir = video_run(output_file, kwargs["roi_locations"], kwargs["preprocess_analysis"])

            analysis_type = kwargs["preprocess_analysis"].replace("_", "-")

            # TODO: Can't install pandas (or pretty much anything) on the RPi, therefore the following 
            # downstream analysis won't work on the local machine (probably good anyways since its so slow)
            # Extract the  Heart and Respiratory Rates
            cmd = f"python3 ../analysis/run_pipeline.py {output_dir} batch_id {analysis_type}"
            subprocess.check_call(cmd, shell=True)

            
#@input_type.command()
#@click.argument()
#def production():
#    pass


if __name__=='__main__':
    input_type()