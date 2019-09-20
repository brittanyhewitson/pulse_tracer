import sys
import json
import click
import logging

import numpy as np

from dbclient.spectrum_metrics import SpectrumApi
from analysis.analyses import FDAnalysis, MatrixAnalysis



# Set up logging
LOGGING_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(format=LOGGING_FORMAT, stream=sys.stderr, level=logging.INFO)


@click.group()
def preprocessing_algorithm():
    pass


@preprocessing_algorithm.command()
@click.argument("json_file", nargs=1)
@click.argument("batch_id", nargs=1)
@click.option("--database", is_flag=True)
def matrix_decomposition(**kwargs):
    """
    """
    if kwargs["database"]:
        spectrum_api = SpectrumApi()

        # Query the database for all ROI with this batch ID
        data = spectrum_api.list_resources(
            "rois", 
            batch_id=kwargs["batch_id"]
        )
    else:
        # Get the data from the JSON file
        with open(kwargs["json_file"], "r") as json_file:
            data = json.load(json_file)

    # Preprocess the data
    roi_analysis = MatrixAnalysis(data=data)

    # Determine the heart rate
    hr = roi_analysis.get_hr()
    logging.info(f"Calculated heart rate is {hr} bpm")

    # Determine the respiratory rate
    rr = roi_analysis.get_rr()
    logging.info(f"Calculated respiratory rate is {rr} breaths")


@preprocessing_algorithm.command()
@click.argument("json_file", nargs=1)
@click.argument("batch_id", nargs=1)
@click.option("--database", is_flag=True)
def fd_bss(**kwargs):
    """
    """
    if kwargs["database"]:
        spectrum_api = SpectrumApi()

        # Query the database for all ROI with this batch ID
        data = spectrum_api.list_resources(
            "rois", 
            batch_id=kwargs["batch_id"]
        )
    else:
        # Get the data from the JSON file
        with open(kwargs["json_file"], "r") as json_file:
            data = json.load(json_file)

    # Preprocess the data
    roi_analysis = FDAnalysis(data=data)

    # Determine the heart rate
    hr = roi_analysis.get_hr()
    logging.info(f"Calculated heart rate is {hr} bpm")

    # Determine the respiratory rate
    rr = roi_analysis.get_rr()
    logging.info(f"Calculated respiratory rate is {rr} breaths")


if __name__=='__main__':
    preprocessing_algorithm()