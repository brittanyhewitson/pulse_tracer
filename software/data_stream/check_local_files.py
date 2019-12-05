import os
import sys
import click
import time
import shutil
import logging

from datetime import datetime

from templates import (
    LOGGING_FORMAT,
    TIMEZONE,
    PREPROCESS_CHOICES,
)
from helpers import (
    run_video_preprocess,
    run_analysis_pipeline,
)

# Set up logging
logging.basicConfig(
    format=LOGGING_FORMAT, 
    stream=sys.stderr, 
    level=logging.INFO
)

@click.command()
@click.argument("input_dir", nargs=1)
@click.argument("roi_locations", nargs=-1)
@click.option("--database", is_flag=True)
@click.option("--preprocess_analysis", default="MD", type=click.Choice(PREPROCESS_CHOICES), help="The preprocessing algorithm used for the downstream analysis")
def main(input_dir, roi_locations, database, preprocess_analysis):
    """

    """
    # Make sure the directory exists
    if not os.path.exists(input_dir):
        raise Exception(f"The input directory {input_dir} does not exist")

    # Make a directory for videos that have been processed
    processed_dir = os.path.join(input_dir, "processed")
    if not os.path.exists(processed_dir):
        os.makedirs(processed_dir)

    num_iter = 0
    while True:
        # Check the for a new file
        files = os.listdir(input_dir)
        files = list(x for x in files if x.endswith(".h264"))

        if num_iter > 300:
            logging.info("No new files for 10 minutes. Terminating analysis")
            break

        if files:
            video_file = os.path.join(input_dir, files[0])
            
            # Process the video data to generate ROI JSON file
            output_dir = run_video_preprocess(
                video_file=video_file,
                roi_locations=roi_locations,
                preprocess_analysis=preprocess_analysis,
                database=database
            )
            
            # Move the video file 
            logging.info(f"Moving video file {video_file} to the processed directory")
            processed_file = os.path.join(processed_dir, files[0])
            shutil.move(video_file, processed_file)
            
            '''
            # Run the analysis pipeline
            run_analysis_pipeline(
                preprocess_analysis=preprocess_analysis,
                json_filepath=output_dir,
            )
            '''
            
        else:
            time.sleep(2)
            num_iter += 1



if __name__=='__main__':
    main()