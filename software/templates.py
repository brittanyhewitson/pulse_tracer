import os
import pytz

# Variables
LOGGING_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
TIMEZONE = pytz.timezone("Canada/Pacific")
SOFTWARE_DIR = os.environ.get("PULSE_TRACER_SOFTWARE_DIR")
#PI_IP = "192.168.1.87" # rpi3 at home
#PI_IP = "142.58.160.36"
PI_IP = "142.58.166.83"

# Choices and Lists
LOCATION_ID_CHOICES = [
    "right_cheek",
    "left_cheek",
    "upper_nose",
    "mid_upper_nose",
    "mid_lower_nose",
    "lower_nose",
    "left_outer_brow",
    "left_mid_outer_brow",
    "left_mid_brow",
    "left_mid_inner_brow",
    "left_inner_brow",
    "right_inner_brow",
    "right_mid_inner_brow",
    "right_mid_brow",
    "right_mid_outer_brow",
    "right_outer_brow",
    "full_face"
]
PREPROCESS_CHOICES = [
    "fd_bss",
    "matrix_decomposition"
]

# Maps
ROI_WORD_TO_NUM_MAP = {
    "right_cheek": "31",
    "left_cheek": "35",
    "upper_nose": "27",
    "mid_upper_nose": "28",
    "mid_lower_nose": "29",
    "lower_nose": "30",
    "left_outer_brow": "17",
    "left_mid_outer_brow": "18",
    "left_mid_brow": "19",
    "left_mid_inner_brow": "20",
    "left_inner_brow": "21",
    "right_inner_brow": "22",
    "right_mid_inner_brow": "23",
    "right_mid_brow": "24",
    "right_mid_outer_brow": "25",
    "right_outer_brow": "26",
}
ROI_NUM_TO_WORD_MAP = {
    "31":"right_cheek",
    "35":"left_cheek",
    "27":"upper_nose",
    "28":"mid_upper_nose",
    "29":"mid_lower_nose",
    "30":"lower_nose",
    "17":"left_outer_brow",
    "18":"left_mid_outer_brow",
    "19":"left_mid_brow",
    "20":"left_mid_inner_brow",
    "21":"left_inner_brow",
    "22":"right_inner_brow",
    "23":"right_mid_inner_brow",
    "24":"right_mid_brow",
    "25":"right_mid_outer_brow",
    "26":"right_outer_brow",
}
