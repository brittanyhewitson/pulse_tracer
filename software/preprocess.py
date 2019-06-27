import sys
import click
import logging

from process_images import process_video

# Set up logging
LOGGING_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(
    format=LOGGING_FORMAT, 
    stream=sys.stderr, 
    level=logging.INFO
)

@click.group()
def input_type():
    pass

@input_type.command()
@click.argument("filename", nargs=1)
def file(**kwargs):
    """
    For testing purposes only -- run the pipeline on an input video

    Args:
        filename:   (str) filepath to the mp4 to be analyzed
    """
    run_preprocess(**kwargs)


@input_type.command()
def stream():
    """
    Process images from a live stream
    """
    pass


def run_preprocess(**kwargs):
    """
    Processes the data before transmitting to the VM to be run through the pipeline
    """
    # Image Processing
    process_video(kwargs["filename"])

    # Data Transmission


if __name__=='__main__':
    input_type()
