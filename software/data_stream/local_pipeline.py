import os
import sys
import click
import subprocess
import logging

import pyodbc
import config
import traceback
import json
import datetime



# Set up logging
LOGGING_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(format=LOGGING_FORMAT, stream=sys.stderr, level=logging.INFO)

@click.command()
@click.argument("filename", nargs=1)
@click.argument("roi_locations", nargs=-1)

# do validation and checks before insert
def validate_string(val):
   if val != None:
        if type(val) is int:
            #for x in val:
            #   print(x)
            return str(val).encode('utf-8')
        else:
            return val

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
	
	# Database authentication
	server = 'capstonesfu.database.windows.net'
	database = 'spectrum_metrics'
	username = 'team2'
	password = '@ensc405'
	driver= '{ODBC Driver 17 for SQL Server}'
	cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password)
	cursor = cnxn.cursor()
	
	# Row iteration through json_file and insert into database
	for i, item in enumerate(json_obj):
		time = item.get("time", None)
		landmark = item.get("landmark", None)
		blue_data = item.get("blue_roi", None)
		blue_data_str = str(blue_data)
	   	green_data = validate_string(item.get("green_roi", None))
		green_data_str = str(green_data)
		red_data = validate_string(item.get("red_roi", None))
		red_data_str = str(red_data)
	 	cursor.execute("INSERT INTO dbo.testing([time],landmark,blue_data,green_data,red_data) VALUES (?,?,?,?,?)", (time,landmark,blue_data_str,green_data_str,red_data_str))

	cnxn.commit()

if __name__=='__main__':
    main()
