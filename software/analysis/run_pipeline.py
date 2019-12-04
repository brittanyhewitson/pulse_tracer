import re
import os
import sys
import json
import click
import logging

import numpy as np

from dbclient.spectrum_metrics import SpectrumApi
from analysis.analyses import FDAnalysis, MatrixAnalysis
from templates import (
    TIMEZONE,
    LOGGING_FORMAT
)

# Set up logging
logging.basicConfig(format=LOGGING_FORMAT, stream=sys.stderr, level=logging.INFO)


@click.group()
def preprocessing_algorithm():
    pass


@preprocessing_algorithm.command()
@click.argument("json_filepath", nargs=1)
@click.argument("batch_id", nargs=1)
@click.option("--database", is_flag=True)
def matrix_decomposition(**kwargs):
    """
    """
    matrix_decomposition_cmd(**kwargs)


def matrix_decomposition_cmd(**kwargs):
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
        batch_re = r"^[\w]*(B\d{5,})[\w]*.json$"
        # Get the data from the JSON filepath
        data = []
        for filename in os.listdir(kwargs["json_filepath"]):
            if filename.endswith(".json"):
                full_path = os.path.join(kwargs["json_filepath"], filename)
                with open(full_path, "r") as json_file:
                    tmp_data = json.load(json_file)
                # Get the batch ID for this data
                if re.match(batch_re, filename, re.I):
                    batch_id = re.match(batch_re, filename, re.I).group(1)
                    for json_data in tmp_data:
                        data.append(json_data)
                else:
                    logging.warning(f"Could not find a batch ID -- skipping JSON file {filename}") 

    # Preprocess the data
    roi_analysis = MatrixAnalysis(data=data)

    # Determine the heart rate
    hr = roi_analysis.get_hr()
    logging.info(f"Calculated heart rate is {hr} bpm")

    # Determine the respiratory rate
    rr = roi_analysis.get_rr()
    logging.info(f"Calculated respiratory rate is {rr} breaths")


@preprocessing_algorithm.command()
@click.argument("json_filepath", nargs=1)
@click.argument("batch_id", nargs=1)
@click.option("--database", is_flag=True)
def fd_bss(**kwargs):
    """
    """
    fd_bss_cmd(**kwargs)


def fd_bss_cmd(**kwargs):
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
        batch_re = r"^[\w]*(B\d{5,})[\w]*.json$"
        # Get the data from the JSON filepath
        data = []
        # TODO: Check that filepath exists
        for filename in os.listdir(kwargs["json_filepath"]):
            if filename.endswith(".json"):
                full_path = os.path.join(kwargs["json_filepath"], filename)
                with open(full_path, "r") as json_file:
                    tmp_data = json.load(json_file)
                # Get the batch ID for this data
                if re.match(batch_re, filename, re.I):
                    batch_id = re.match(batch_re, filename, re.I).group(1)
                    for json_data in tmp_data:
                        data.append(json_data)
                else:
                    logging.warning(f"Could not find a batch ID -- skipping JSON file {filename}")  

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