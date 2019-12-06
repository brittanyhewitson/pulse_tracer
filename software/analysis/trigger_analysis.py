import os
import sys
import time
import click
import logging
import subprocess

import numpy as np

from operator import itemgetter

from dbclient.spectrum_metrics import SpectrumApi, PostError, NotFoundError
from templates import (
    TIMEZONE,
    LOGGING_FORMAT
)
from analysis.run_pipeline import matrix_decomposition_cmd, fd_bss_cmd

spectrum_api = SpectrumApi()

# Set up logging
logging.basicConfig(
    format=LOGGING_FORMAT, 
    stream=sys.stderr, 
    level=logging.INFO
)


def check_roi(max_iter=300, wait_time=2):
    """
    """
    # TODO: In phase III, remove this loop and run with the entire script with a cron job
    max_wait_time = (max_iter * wait_time) / 60 
    num_iter = 0
    while True:
        # If we have been waiting for longer than the max wait time
        if num_iter > max_iter:
            logging.info(f"No new data for {max_wait_time} minutes. Terminating analysis")
            break

        # Query the database for all unanalyzed ROIs
        logging.info("Querying the database for batches to analyze")
        batches = spectrum_api.list_resources(
            "batches", 
            analyzed=False,
        )
        # TODO: The following will be used instead of querying for batches
        #       once we introduce windowing
        '''
        rois = spectrum_api.list_resources(
            "rois", 
            analysis_in_progress=False,
            hr_analyzed=False
        )
        '''

        try:
            # Determine unique batch IDs that need analysis
            batch_ids = sorted(list(set(map(itemgetter("id"), batches))))
            # TODO: Use the following once we introduce windowing
            #batch_ids = sorted(list(set(map(itemgetter("batch"), rois))))
        except NotFoundError:
            # Continue the loop if there are no ROIs to analyze
            logging.info(f"No batches to analyze at this time. Waiting for {wait_time} seconds")
            time.sleep(wait_time)
            num_iter += 1
            continue
        
        # Trigger analysis for each batch
        analyze_roi(batch_ids, wait_time)
        num_iter = 0


def analyze_roi(batch_ids, wait_time):
    """
    """    
    # Run the analysis pipeline
    for batch_id in batch_ids:
        # Get the batch object
        batch = spectrum_api.get(
            "batches", 
            id=batch_id
        )
        try:
            rois = spectrum_api.list_resources(
                "rois",
                batch__id=batch_id
            )
            rois_list = list(set(map(itemgetter("id"), rois)))
        except NotFoundError:
            logging.info(f"No ROIs to analyze at this time. Waiting for {wait_time} seconds")
            time.sleep(wait_time)
            return

        logging.info(f"Running analysis for batch {batch_id}")
        if batch["preprocessing_analysis"] == "MD":
            hr, rr = matrix_decomposition_cmd(
                batch_id=batch_id,
                database=True
            )
        else:
            hr, rr = fd_bss_cmd(
                batch_id=batch_id,
                database=True
            )
        
@click.command()
@click.option("--max_iter", default=300)
@click.option("--wait_time", default=2)
def main(max_iter, wait_time):
    check_roi(max_iter, wait_time)
 
if __name__=='__main__':
    check_roi()
