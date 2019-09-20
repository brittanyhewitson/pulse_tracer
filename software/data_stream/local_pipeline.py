import os
import sys
import click
import subprocess
import logging

# Set up logging
LOGGING_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(format=LOGGING_FORMAT, stream=sys.stderr, level=logging.INFO)

@click.command()
@click.argument("filename", nargs=1)
@click.argument("roi_locations", nargs=-1)
def main(filename, roi_locations):
    # Check that the file exists
    if not os.path.exists(filename):
        raise Exception("The supplied file does not exist")

    # If this is the raw data, convert to MP4
    if filename.endswith(".h264"):
        logging.info("Creating mp4 from h264")
        mp4_file = filename.strip(".h264") + ".mp4"
        cmd = f"MP4Box -fps 30 -add {filename} {mp4_file}"
        subprocess.check_call(cmd, shell=True)
    elif filename.endswith(".mp4"):
        mp4_file = filename
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