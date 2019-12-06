import os
import re
import sys
import click
import logging

import pandas as pd

from analysis.run_pipeline import matrix_decomposition_cmd, fd_bss_cmd
from templates import (
    PREPROCESS_CHOICES,
    LOGGING_FORMAT,
    LOCATION_ID_CHOICES
)
from data_stream.helpers import (
    run_video_preprocess,
    run_analysis_pipeline,
)

# Set up logging
logging.basicConfig(format=LOGGING_FORMAT, stream=sys.stderr, level=logging.INFO)

@click.command()
@click.argument("input_dir", nargs=1)
def run_test(**kwargs):
    video_filenames = os.listdir(kwargs['input_dir'])
    video_filenames = list(x for x in video_filenames if x.endswith(".h264"))

    
    for video_filename in video_filenames:
        run_names, hrs, rrs, rois, preprocessings = [], [], [], [], []
        for roi_location in LOCATION_ID_CHOICES:
            for preprocess in PREPROCESS_CHOICES:
                if roi_location == "full_face":
                    continue
                logging.info(f"PROCESSING {roi_location} USING {preprocess}")
                video_file = os.path.join(kwargs["input_dir"], video_filename)
                # Process the video data to generate ROI JSON file
                logging.info(f"Processing {video_file}")
                output_dir = run_video_preprocess(
                    video_file=video_file,
                    roi_locations=[roi_location],
                    preprocess_analysis=preprocess,
                    database=False,
                )

                # Run the analysis pipeline
                hr, rr = run_analysis_pipeline(
                    preprocess_analysis=preprocess,
                    json_filepath=output_dir,
                )

                run_names.append(video_filename)
                hrs.append(hr)
                rrs.append(rr)
                rois.append(roi_location)
                preprocessings.append(preprocess)

        df = pd.DataFrame({
            "run_name": run_names,
            "heart_rate": hrs,
            "resp_rate": rrs,
            "roi": rois,
            "preprocessing": preprocessings
        })

        df.to_csv(os.path.join(kwargs["input_dir"], f"{video_filename}_test_results.csv"), index=False)


if __name__=='__main__':
    run_test()
