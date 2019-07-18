import cv2
import sys
import time
import json
import click
import timeit
import logging

from process_images import ProcessVideo

# Set up logging
LOGGING_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(
    format=LOGGING_FORMAT, 
    stream=sys.stderr, 
    level=logging.INFO
)


def get_video_roi_data(filename):
    """
    Processes a video to extract ROI at each frame in the clip

    Args:
        filename:   (str) full path to the video
    Returns:
        process_video.rois: (list) a list of dicts holding landmark info,
                            the time of the frame, and the ROI data
    """
    process_video = ProcessVideo(filename)

    # Time the algorithm
    start = timeit.default_timer()
    while(True):
        # Read the video
        ret, frame = process_video.video.read()
        if frame is None:
            break

        # Add frame info to the class
        process_video.frame = frame
        process_video.gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        process_video.frame_time = time.time()

        # Detect the face
        faces = process_video.detect_faces()
        if len(faces) == 0:
            continue

        # Need to add function for comparing multiple detected faces here

        # Get the landmarks
        process_video.get_landmarks(faces)

        # Show the image
        cv2.imshow('frame', process_video.frame)

        # Break if the "q" key is selected
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    # Log how long the algorithm took
    stop = timeit.default_timer()
    total_time = stop - start
    logging.info("Total time was %s" % total_time)
    
    # When everything done, release the capture
    process_video.video.release()
    cv2.destroyAllWindows()

    # Save roi as json 
    dest_file = filename.strip(".mp4") 
    with open(f"{dest_file}.json", "w") as filename:
        json.dump(process_video.rois, filename)

    return process_video.rois


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
    Processes the data and then transmits to the VM for analysis

    Args:
        kwargs: (dict) contains filename, which is the full path to the
                video file
    """
    # Image Processing
    data = get_video_roi_data(kwargs["filename"])
    
    # Data Transmission


if __name__=='__main__':
    input_type()
