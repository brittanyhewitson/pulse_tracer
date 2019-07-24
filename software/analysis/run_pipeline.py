import sys
import json
import click
import logging

from heart_rate import HeartRate
from resp_rate import RespRate

#temp
import matplotlib.pyplot as plt

# Set up logging
LOGGING_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(format=LOGGING_FORMAT, stream=sys.stderr, level=logging.INFO)


@click.command()
@click.argument("json_file", nargs=1)
def main(json_file):
    # Get data
    # Until the pipeline is set up, this will just be 
    # a json file that is the output of the preprocessing algorithm
    with open(json_file, "r") as json_file:
        data = json.load(json_file)

    # Begin Heart Rate Extraction
    heart_rate_processing = HeartRate(data=data)
    
    resp_rate_processing = RespRate()
    
    heart_rate = heart_rate_processing.determine_heart_rate()
    
    resp_rate = resp_rate_processing.determine_resp_rate(heart_rate_processing.get_average_signal())

    logging.info(f"The heart rate for this video is {heart_rate} bpm")
    
    logging.info(f"The respiratory rate for this video is {resp_rate} bpm")
    
if __name__=='__main__':
    main()