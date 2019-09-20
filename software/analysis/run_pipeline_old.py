import sys
import json
import click
import logging

import numpy as np
from scipy.signal import butter, filtfilt

from dbclient.spectrum_metrics import SpectrumApi
from heart_rate import HeartRate
from resp_rate import RespRate

#temp
import matplotlib.pyplot as plt

# Set up logging
LOGGING_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(format=LOGGING_FORMAT, stream=sys.stderr, level=logging.INFO)


@click.command()
@click.argument("json_file", nargs=1)
#@click.argument("batch_id", nargs=1)
@click.option("--database", is_flag=True)
def main(**kwargs):
    
    if kwargs["database"]:
        spectrum_api = SpectrumApi()

        # Query the database for all ROI with this batch ID
        data = spectrum_api.list_resources(
            "rois",
            batch_id=kwargs["batch_id"],
        )
        
    else:
        # Get data
        # Until the pipeline is set up, this will just be 
        # a json file that is the output of the preprocessing algorithm
        with open(kwargs["json_file"], "r") as json_file:
            data = json.load(json_file)
    
    # Begin Heart Rate Extraction
    heart_rate_processing = HeartRate(data=data)
    
    resp_rate_processing = RespRate()
    
    heart_rate = heart_rate_processing.determine_heart_rate()
    
    resp_rate = resp_rate_processing.determine_resp_rate(heart_rate_processing.get_average_signal())

    logging.info(f"The heart rate for this video is {heart_rate} bpm")
    
    logging.info(f"The respiratory rate for this video is {resp_rate} breaths")
    
if __name__=='__main__':
    main()