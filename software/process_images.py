import sys
import cv2
import click
import timeit
import logging
import matplotlib.pyplot as plt

# Set up logging
LOGGING_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(format=LOGGING_FORMAT, stream=sys.stderr, level=logging.INFO)

COLOURS = [
    (0, 255, 0), 
    (255, 0, 0),
    (0, 0, 255)
]

TRAINED_XMLS = [
    'data/haarcascade_frontalface_default.xml',
    'data/haarcascade_frontalface_alt.xml',
    'data/haarcascade_frontalface_alt2.xml'
    'data/haarcascade_profileface.xml'
]

#--------------------------------------------------------------------
#------------------------- Helper functions -------------------------
#--------------------------------------------------------------------
def detect_faces(image, classifier_file):
    haar_cascade_face = cv2.CascadeClassifier(classifier_file)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces_rect = haar_cascade_face.detectMultiScale(
            gray_image, 
            scaleFactor=1.1, 
            minNeighbors=5,
            minSize=(100, 100)
        )
    return faces_rect


def draw_rectangle(image, faces, colour):
    for (x, y, w, h) in faces:
        logging.debug(faces)
        cv2.rectangle(image, (x, y), (x+w, y+h), colour, 2)


@click.command()
@click.argument("filename", nargs=1)
def process_video_cmd(filename):
    process_video(filename)

def process_video(filename):
    """
    Image processing steps. Includes facial recognition, 
    and determining the ROI

    Args:
        filename:   (str) filepath to the mp4 video to be analyzed
    """
    logging.info("Reading video file")
    video = cv2.VideoCapture(filename)
    
    # Time the algorithm
    start = timeit.default_timer()
    while(True):
        ret, frame = video.read()
        if frame is None:
            break

        # Try all of the XMLS until a face is detected
        for i in range(len(TRAINED_XMLS)):
            faces_rect = detect_faces(frame, TRAINED_XMLS[i])
            colour = COLOURS[i]

            if len(faces_rect) > 0:
                break
        
        # If no matches found, go to the next frame
        if len(faces_rect) == 0:
            continue

        # Compare the new rectangles with the previous frame. Because we are processing
        # a video at 30fps, there should not be much variation between the two frames. 
        # Therefore, select the rectangle that is closest to the preious frame
        #compare_rectangles()

        # Draw the rectangle on the frame (only for testing and demo)
        draw_rectangle(frame, faces_rect, colour)
        
        # Show the detected face
        cv2.imshow('frame', frame)
        
        # Break if the "q" key is selected
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Log how long the algorithm took
    stop = timeit.default_timer()
    total_time = stop - start
    logging.info("Total time was %s" % total_time)
    
    # When everything done, release the capture
    video.release()
    cv2.destroyAllWindows()

if __name__=="__main__":
    process_video_cmd()

