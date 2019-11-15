# Pulse Tracer

Pulse Tracer is a patient monitoring system created by LumoAnalytics. It uses photoplethysmography (PPG) to remotely measure the heart and respiratory rates of primarily immobile elderly patients who are often left unattended. The goal of the device is to provide a way to accurately measure the heart and respiratory rates of patients and to detect significant variations from the average values in an attempt to alert caregivers of possible emerging health conditions.

Pulse Tracer consists of three major components:
1.  **Physical Pulse Tracer device for collecting data**
    * currently a Raspberry Pi 4 with a Raspberry Pi NoIR camera
2.  **Pulse Tracer Pipeline**
    * a preprocessing pipeline [located here](https://csil-git1.cs.surrey.sfu.ca/capstone-1194-group-2/capstone/tree/master/software/data_stream) to perform facial detection and region of interest (ROI) selection on raw data from the Raspberry Pi camera
    * a script to query the remote database for new data and supsequently launch downstream analysis
    * an analysis pipeline [located here](https://csil-git1.cs.surrey.sfu.ca/capstone-1194-group-2/capstone/tree/master/software/analysis) to determine the heart and respiratory rates from the ROI data stored in the database

3.  **Spectrum Metrics Web Application**
    * a web application [located here](https://csil-git1.cs.surrey.sfu.ca/capstone-1194-group-2/capstone/tree/master/software/spectrum_metrics), built from Django to provide users the ability to view their data

The following guide will show you how to setup the Pulse Tracer pipeline and Spectrum Metrics web application.

## Installing Pulse Tracer Software
First, install virutalenv for python 3.7:
```
pip install virtualenv
```

Next, create an environment and activate it:
```
virtualenv pulse_tracer
source pulse_tracer/bin/activate
```
  
Go into the software directory and install the requirements:
```
cd capstone/software
pip install -r requirements.txt
```
  
Setup
```
python setup.py develop
```
  
## Environment Variables
In order to run the Pulse Tracer pipeline and access the Azure database, certain variables must be set. The following table identifies which variables need to be set on each machine, namely the Raspberry Pi running the preprocessing script, the machine running the Spectrum Metrics web application, and the machine running the downstream data analysis pipeline. Note that the variables required by the Raspberry Pi will also need to be set on your local machine if you launch the data collection script remotely. 

| Variable | Raspberry Pi | Spectrum Metrics machine | Analysis machine |
| --------- | :-----------: | :-----------------------: | :---------------: |
| `DEVICE_SERIAL_NUMBER` | :heavy_check_mark: | | | |
| `DEVICE_MODEL` | :heavy_check_mark: | | | |
| `AZURE_DB_USER` | :heavy_check_mark: | | | |
| `AZURE_DB` | :heavy_check_mark: | | | |
| `AZURE_DB_USERNAME` |:heavy_check_mark: | | | |
| `AZURE_DB_PASSWORD` | :heavy_check_mark: | | | |
| `SPECTRUM_METRIC_API_USERNAME` | | :heavy_check_mark: | :heavy_check_mark: |
| `SPECTRUM_METRIC_API_PASSWORD` | | :heavy_check_mark: | :heavy_check_mark: |
| `SPECTRUM_METRIC_API_URL` | | :heavy_check_mark: | :heavy_check_mark: |

Where `SPECTRUM_API_USERNAME` and `SPECTRUM_API_PASSWORD` are your credentials associated with the Spectrum Metrics Django app, and `DEVICE_SERIAL_NUMBER` and `DEVICE_MODEL` correspond to the serial number and model of the Pulse Tracer device running the code
  
## Database Objects
Ensure you have created the following objects in the Spectrum Metrics web app before you run the pipeline:
* **Device** - a device object with the same serial number and model as the Pulse Tracer device  
* **Health Care Provider** - a health care provider to be associated with the patient  
* **Patient** - a patient associated with the above health care provider and device 

## Running the Preprocessing Pipeline
The following sections will outline how to launch the Pulse Tracer pipeline. This can be launched from either your local machine, or on the Raspberry Pi. If you're launching from a local machine, make sure you are able to successfully SSH into your Raspberry Pi so you can remotely launch the data collection script.
 
 The recorded video can either be processed as a video file with a specified length, or as a live stream. The former saves the data as an `.h264` file with a finite length, whereas the latter selects frames from the stream to process in real time. Both produce a JSON file containing ROI data from the video. 

To record a video on the Raspberry Pi, the `rpi_camera_collect.py` script can be used as follows:
```
python3 rpi_camera_collect.py /path/to/output/video1.h254 --video_length 15
```
This script will save the video as an `.h264` file, however the preprocessing pipeline will also accept video files in the `.mp4` file format.

### Running the Pipeline on the Raspberry Pi
#### Video Analysis
To run the preprocessing analysis on an existing video file, you will need to run the `preprocess.py` script with the `video-file` command, which has the following inputs:

| Input | Type | Description | Required |
| ----- | ---- | ----------- | :------: |
| `filename` | string | The name of the input video file | :heavy_check_mark: |
| `roi_locations` | list of strings | A list of the ROIs to use in the preprocessing algorithm. The options for these regions can be found [here](https://csil-git1.cs.surrey.sfu.ca/capstone-1194-group-2/capstone/blob/master/software/templates.py#L13) | :heavy_check_mark: |
| `--matrix_decomposition` | flag | A flag specifying whether to use the matrix decomposition algorithm for downstream analysis or to use FDBSS | :x: |
| `--database` | flag | A flag specifying whether to send the ROI data to the Azure database | :x: |

An example of this using the matrix decomposition algorithm is:
```
python3 preprocess.py video-file /path/to/video_1.h264  left_cheek right_cheek --matrix_decomposition
```

#### Stream Analysis
  To run the preprocessing analysis on a live stream, you will need to run the `preprocess.py` script with the `video-stream` command, which has the following inputs:
  
| Input | Type | Description | Required |
| ----- | ---- | ----------- | :------: |
| `roi_locations` | list of strings | A list of the ROIs to use in the preprocessing algorithm. The options for these regions can be found [here](https://csil-git1.cs.surrey.sfu.ca/capstone-1194-group-2/capstone/blob/master/software/templates.py#L13) | :heavy_check_mark: |
| `--data_dir` | string | A filepath to the directory where the JSON data will be stored. The default value is the directory where the code is | :x: |
| `--matrix_decomposition` | flag | A flag specifying whether to use the matrix decomposition algorithm for downstream analysis or to use FDBSS | :x: |
| `--database` | flag | A flag specifying whether to send the ROI data to the Azure database | :x: |
| `--remote_output_dir` | string | If the JSON files are to be transferred from the Raspberry Pi to a remote machine, this directory specifies the location on the remote machine | :x: |
| `--remote_host` | string | If the JSON files are to be transferred from the Raspberry Pi to a remote machine, this specifies the name of the host in the `config` file on the Raspberry Pi. Note that passwordless SSH must be setup from the Raspberry Pi to this host. | :x: |

An example of this using the matrix decomposition algorithm is:
```
python3 preprocess.py video-stream  left_cheek right_cheek --matrix_decomposition --data_dir /home/pi/Desktop/
```

### Running the Pipeline on a Local Machine
#### Video Analysis on Existing Video File
To run the preprocessing analysis on an existing video file, you will need to run the `local_pipeline.py` script with the `local-video` command, which has the following inputs:

| Input | Type | Description | Required |
| ----- | ---- | ----------- | :------: |
| `roi_locations` | list of strings | A list of the ROIs to use in the preprocessing algorithm. The options for these regions can be found [here](https://csil-git1.cs.surrey.sfu.ca/capstone-1194-group-2/capstone/blob/master/software/templates.py#L13) | :heavy_check_mark: |
| `--input_file` | string | The filepath to the existing video file on the local machine | :heavy_check_mark: |
| `--preprocess_analysis` | string | Specifies whether to use matrix decomposition or FDBSS for the preprocessing algorithm. Choices for this field can be found [here](https://csil-git1.cs.surrey.sfu.ca/capstone-1194-group-2/capstone/blob/master/software/templates.py#L32). The default value is FDBSS | :x: | 
| `--database` | flag | a flag specifying whether to send the ROI data to the Azure database instead of storing a JSON file on the local machine | :x: |

An example of using this with the matrix decomposition algorithm is:
```
python3 local_pipeline.py local-video left_cheek right_cheek --input_file /path/to/existing/video1.h264 --preprocess_analysis matrix_decomposition
```
#### Remote Data Collection and Video Analysis
To remotely launch data collection run the preprocessing analysis on the resulting video file, you will need to run the `local_pipeline.py` script with the `remote-video` command, which has the following inputs:

| Input | Type | Description | Required |
| ----- | ---- | ----------- | :------: |
| `roi_locations` | list of strings | A list of the ROIs to use in the preprocessing algorithm. The options for these regions can be found [here](https://csil-git1.cs.surrey.sfu.ca/capstone-1194-group-2/capstone/blob/master/software/templates.py#L13) | :heavy_check_mark: |
| `--output_filename` | string | The filename to give the resulting JSON file | :x: |
| `--destination_filepath` | string | The filepath to the directory where the JSON file will be stored on the local machine | :x: |
| `--preprocess_analysis` | string | Specifies whether to use matrix decomposition or FDBSS for the preprocessing algorithm. Choices for this field can be found [here](https://csil-git1.cs.surrey.sfu.ca/capstone-1194-group-2/capstone/blob/master/software/templates.py#L32). The default value is FDBSS | :x: | 
| `--video_length` | int | The length of the video to record (in seconds). The default value is 30 | :x: |
| `--database` | flag | a flag specifying whether to send the ROI data to the Azure database instead of storing a JSON file on the local machine | :x: |

An example of using this with the matrix decomposition algorithm is:
```
python3 local_pipeline.py remote-video left_cheek right_cheek --output_filename output_json_filename --destination_filepath /path/to/output/dir/on/local --preprocess_analysis matrix_decomposition --video_length 15
```
#### Stream Analysis
To remotely launch data collection run the preprocessing analysis on the resulting video file, you will need to run the `local_pipeline.py` script with the `remote-stream` command, which has the following inputs:

 Input | Type | Description | Required |
| ----- | ---- | ----------- | :------: |
| `destination_filepath` | string | The full filepath to where the video file will be stored | :heavy_check_mark: |
| `roi_locations` | list of strings | A list of the ROIs to use in the preprocessing algorithm. The options for these regions can be found [here](https://csil-git1.cs.surrey.sfu.ca/capstone-1194-group-2/capstone/blob/master/software/templates.py#L13) | :heavy_check_mark: |
| `--preprocess_analysis` | string | Specifies whether to use matrix decomposition or FDBSS for the preprocessing algorithm. Choices for this field can be found [here](https://csil-git1.cs.surrey.sfu.ca/capstone-1194-group-2/capstone/blob/master/software/templates.py#L32). The default value is FDBSS | :x: | 
| `--database` | flag | a flag specifying whether to send the ROI data to the Azure database instead of storing a JSON file on the local machine | :x: |

An example of using this with the matrix decomposition algorithm is:
```
python3 local_pipeline.py remote-stream /path/to/local/dir/ left_cheek right_cheek --preprocess_analysis matrix_decomposition --video_length 15
```