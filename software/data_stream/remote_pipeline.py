import os
import sys
import click
import subprocess
import logging
import paramiko
import time

# Set up logging
LOGGING_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(format=LOGGING_FORMAT, stream=sys.stderr, level=logging.INFO)

@click.command()
@click.argument("filename", nargs=1)
@click.argument("destination_filepath", nargs=1)
@click.argument("roi_locations", nargs=-1)
def main(filename, destination_filepath, roi_locations):
    logging.info("Connecting to Raspberry Pi")
    # Connect to the client
    ssh_client = paramiko.SSHClient()
    ssh_client.load_system_host_keys()
    ssh_client.connect("142.58.161.27", username="pi")

    remote_output_file = os.path.join("/home/pi/Desktop", filename + ".h264")
    local_output_file = os.path.join(destination_filepath, filename + ".h264")
    cmd = f"python /home/pi/Desktop/remote_camera.py {remote_output_file}"
    
    logging.info("Launching data collection on Raspberry Pi")
    stdin, stdout, stderr = ssh_client.exec_command(cmd)

    time.sleep(20)

    logging.info("Copying video file to local")
    # Rsync the file from remote to local
    cmd = f"rsync -avPL pi@142.58.161.27:{remote_output_file} {local_output_file}"
    subprocess.check_call(cmd, shell=True)
    ssh_client.close()

    # Check that the file exists
    if not os.path.exists(local_output_file):
        raise Exception("The supplied file does not exist")

    # If this is the raw data, convert to MP4
    if local_output_file.endswith(".h264"):
        logging.info("Creating mp4 from h264")
        mp4_file = local_output_file.strip(".h264") + ".mp4"
        cmd = f"MP4Box -fps 30 -add {local_output_file} {mp4_file}"
        subprocess.check_call(cmd, shell=True)
    elif local_output_file.endswith(".mp4"):
        mp4_file = local_output_file
    else:
        raise Exception("Unrecognized file format")

    json_output = mp4_file.strip(".mp4") + ".json"

    # Check if the JSON file already exists
    if not os.path.exists(json_output):
        logging.info("Running preprocess to determine ROI")
        # Run the Preprocessing algorithm to get ROIs
        cmd = f"python preprocess.py file {mp4_file}"
        for roi_location in roi_locations:
            cmd += f" {roi_location}"
        subprocess.check_call(cmd, shell=True)
    else:
        logging.info("ROI JSON file already exists")

    # Check that the JSON output was successfully created
    assert os.path.exists(json_output)

    # Extract the  Heart and Respiratory Rates
    cmd = f"python ../analysis/run_pipeline.py {json_output}"
    subprocess.check_call(cmd, shell=True)

if __name__=='__main__':
    main()

