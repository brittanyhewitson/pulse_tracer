import paramiko
import logging
from data_stream.preprocess import video_stream_cmd, video_file_cmd
from analysis.run_pipeline import matrix_decomposition_cmd, fd_bss_cmd

from templates import PI_IP

from pynput.keyboard import Key, Listener


def on_press(key):
    print(f"{key} pressed")


def on_release(key):
    print(f"{key} released")
    if key == Key.esc:
        return False
 

def connect_to_client():
    """
    Connects to the Raspberry Pi via SSH 
    """
    # Connect to the client
    ssh_client = paramiko.SSHClient()
    ssh_client.load_system_host_keys()
    ssh_client.connect(PI_IP, username="pi")
    return ssh_client


def run_analysis_pipeline(preprocess_analysis, json_filepath, database=False):
    """
    Runs the data analysis given a filepath to a JSON file holding the ROI data
    """
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