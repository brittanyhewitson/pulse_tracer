import sys
import cv2
import dlib
import click
import timeit
import logging
import matplotlib.pyplot as plt

from math import floor, sqrt

# Set up logging
LOGGING_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(format=LOGGING_FORMAT, stream=sys.stderr, level=logging.INFO)

COLOURS = [
    (0, 255, 0), 
    (255, 0, 0),
    (0, 0, 255),
    (255, 0, 255)
]

TRAINED_XMLS = [
    'data/haarcascade_frontalface_default.xml',
    'data/haarcascade_frontalface_alt.xml',
    'data/haarcascade_frontalface_alt2.xml',
    'data/haarcascade_profileface.xml'
]

#--------------------------------------------------------------------
#------------------------- Helper functions -------------------------
#--------------------------------------------------------------------
def detect_faces(image, haar_cascade_face):
    faces_rect = haar_cascade_face.detectMultiScale(
            image, 
            scaleFactor=1.1, 
            minNeighbors=5,
            minSize=(100, 100)
        )
    return faces_rect


def draw_rectangle(image, faces, colour):
    for (x, y, w, h) in faces:
        logging.debug(faces)
        cv2.rectangle(image, (x, y), (x+w, y+h), colour, 2)


def get_landmark(landmarks, frame, landmark_range, roi_size, vert_translation, hor_translation):
    rois = []
    for n in landmark_range:
        x_n = landmarks.part(n).x
        y_n = landmarks.part(n).y
        cv2.circle(frame, (x_n, y_n), 2, (255, 0, 0), -1)

        x1 = x_n + hor_translation + roi_size
        x2 = x_n + hor_translation - roi_size
        y1 = y_n + vert_translation + roi_size
        y2 = y_n + vert_translation - roi_size
        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 0), 2)
        
        rois.append(frame[x2:x1, y2:y1])
    return rois
        

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

    # Get the predictor
    predictor = dlib.shape_predictor("data/shape_predictor_68_face_landmarks.dat")
    
    haar_cascade_faces = []
    for trained_xml in TRAINED_XMLS:
        haar_cascade_faces.append(cv2.CascadeClassifier(trained_xml))

    # Time the algorithm
    start = timeit.default_timer()
    while(True):
        ret, frame = video.read()
        if frame is None:
            break
        '''
        # Rotate image (testing only)
        rows, cols, color = frame.shape
        M = cv2.getRotationMatrix2D((cols/2, rows/2), 270, 1)
        frame = cv2.warpAffine(frame, M, (cols, rows))
        '''
        gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Try all of the XMLS until a face is detected
        for i in range(len(TRAINED_XMLS)):
            faces_rect = detect_faces(gray_image, haar_cascade_faces[i])
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

        # Determing facial landmarks
        for (x, y, w, h) in faces_rect:
            face = dlib.rectangle(x, y, w+x, h+y)
            landmarks = predictor(gray_image, face)
            
            # Determine how big the regions of interest should be
            pixel_area = 0.005 * face.area()
            pixel_size = floor(sqrt(pixel_area)/2)
            forehead_vert_translation = pixel_size
            cheek_translation = floor(sqrt(0.05 * face.area())/2)

            # Look at landmarks on the bridge of the nose
            nose_roi = get_landmark(
                landmarks, 
                frame, 
                range(27, 31),
                pixel_size, 
                forehead_vert_translation, 
                0
            )

            # Look at landmarks on the forehead
            forehead_roi = get_landmark(
                landmarks, 
                frame, 
                range(17, 27),
                pixel_size, 
                -forehead_vert_translation, 
                0
            )

            # Look at landmarks on the cheeks
            left_cheek_roi = get_landmark(
                landmarks, 
                frame, 
                range(32, 33),
                pixel_size, 
                0, 
                -cheek_translation
            )

            right_cheek_roi = get_landmark(
                landmarks, 
                frame, 
                range(35, 36),
                pixel_size, 
                0, 
                cheek_translation
            )

            '''
            for i in right_cheek_roi:
                cv2.imshow('frame', i)
            break
            '''

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

