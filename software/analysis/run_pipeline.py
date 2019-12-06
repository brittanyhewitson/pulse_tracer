import re
import os
import sys
import json
import click
import logging

import numpy as np
from datetime import datetime

from dbclient.spectrum_metrics import SpectrumApi, PostError
from analysis.analyses import FDAnalysis, MatrixAnalysis
from templates import (
    TIMEZONE,
    LOGGING_FORMAT
)

# Set up logging
logging.basicConfig(format=LOGGING_FORMAT, stream=sys.stderr, level=logging.INFO)

spectrum_api = SpectrumApi()


def update_analysis(analysis, batch):
    """
    THIS WILL BE USED ONCE WE INTRODUCE WINDOWING, BUT FOR NOW THERE IS NO WINDOWING
    SO WE ANALYZE ONE BATCH AT A TIME INSTEAD
    """
    # Gather all rois in batch
    rois = spectrum_api.list_resources(
        "rois", 
        batch__id=batch
    )
    
    if analysis == 'hr':
        hr_analyzed = True
        rr_analyzed = False
        in_progress = True
    elif analysis == 'rr':
        hr_analyzed = True
        rr_analyzed = True
        in_progress = False
    else:
        logging.error(f"Unrecognized analysis type {analysis}. Skipping update")
        return 
    try:
        # update each roi
        for roi in rois:
            roi_updated = spectrum_api.update(
                    "rois",
                    roi['id'],
                    hr_analyzed=hr_analyzed,
                    rr_analyzed=rr_analyzed,
                    analysis_in_progress=in_progress
                )
    except PostError as p:
        logging.error(p.msg)
    except:
        logging.info("Reattempt analysis on subsequent script call")
    

@click.group()
def preprocessing_algorithm():
    pass


@preprocessing_algorithm.command()
@click.option("--json_filepath")
@click.option("--batch_id")
@click.option("--database", is_flag=True)
def matrix_decomposition(**kwargs):
    """
    """
    matrix_decomposition_cmd(**kwargs)


def matrix_decomposition_cmd(**kwargs):
    """
    """
    if kwargs["database"]:
        # Query the database for all ROI with this batch ID
        data = spectrum_api.list_resources(
            "rois", 
            batch__id=kwargs["batch_id"]
        )

        batch = spectrum_api.get(
            "batches",
            id=kwargs["batch_id"]
        )
        patient = spectrum_api.get(
            "patients",
            device=batch["device"]
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

    if kwargs["database"]:
        # Create a HR object
        hr_object = spectrum_api.create(
            "heart_rates",
            heart_rate=round(hr, 2),
            analyzed_time=datetime.now(TIMEZONE).isoformat(),
            batch=kwargs["batch_id"],
            patient=patient["id"]
        )
        # TODO: Update the analysis once we introduce windowing
        '''
        # Update the analysis
        update_analysis("hr", kwargs["batch_id"])
        '''

    # Determine the respiratory rate
    rr = roi_analysis.get_rr()
    logging.info(f"Calculated respiratory rate is {rr} breaths")

    if kwargs["database"]:
        # Create a RR object
        rr_object = spectrum_api.create(
            "respiratory_rates",
            respiratory_rate=round(rr, 2),
            analyzed_time=datetime.now(TIMEZONE).isoformat(),
            batch=kwargs["batch_id"],
            patient=patient["id"]
        )
        '''
        # Update the analysis
        update_analysis("rr", kwargs["batch_id"])
        '''
        # TODO: Remove this and use the above update once we introduce windowing
        try:
            # Update the batch
            batch_update = spectrum_api.update(
                "batches",
                id=kwargs["batch_id"],
                analyzed=True,
            )
        except PostError as p:
            logging.error(p.msg)
        except:
            logging.error("Reattempt analysis on subsequent script call")


@preprocessing_algorithm.command()
@click.option("--json_filepath")
@click.option("--batch_id")
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
            batch__id=kwargs["batch_id"]
        )
        batch = spectrum_api.get(
            "batches",
            id=kwargs["batch_id"]
        )
        patient = spectrum_api.get(
            "patients",
            device=batch["device"]
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

    if kwargs["database"]:
        # Create a HR object
        hr_object = spectrum_api.get_or_create(
            "heart_rates",
            heart_rate=round(hr, 2),
            analyzed_time=datetime.now(TIMEZONE).isoformat(),
            batch=kwargs["batch_id"],
            patient=patient["id"]
        )
        # TODO: Update the analysis once we introduce windowing
        '''
        # Update the analysis
        update_analysis("hr", kwargs["batch_id"])
        '''

    # Determine the respiratory rate
    rr = roi_analysis.get_rr()
    logging.info(f"Calculated respiratory rate is {rr} breaths")

    if kwargs["database"]:
        # Create a RR object
        rr_object = spectrum_api.get_or_create(
            "respiratory_rates",
            respiratory_rate=round(rr, 2),
            analyzed_time=datetime.now(TIMEZONE).isoformat(),
            batch=kwargs["batch_id"],
            patient=patient["id"]
        )
        '''
        # Update the analysis
        update_analysis("rr", kwargs["batch_id"])
        '''
        # TODO: Remove this and use the above update once we introduce windowing
        try:
            # Update the batch
            batch_update = spectrum_api.update(
                "batches",
                id=kwargs["batch_id"],
                analyzed=True,
            )
        except PostError as p:
            logging.error(p.msg)
        except:
            logging.error("Reattempt analysis on subsequent script call")


if __name__=='__main__':
    preprocessing_algorithm()