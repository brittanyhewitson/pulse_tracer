# Pulse Tracer

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
In order to run the Pulse Tracer pipeline and access the Azure database, the following environment variables must be set
```
SPECTRUM_API_USERNAME
SPECTRUM_API_PASSWORD
SPECTRUM_API_URL
DEVICE_SERIAL_NUMBER
DEVICE_MODEL
```

Where `SPECTRUM_API_USERNAMEY` and `SPECTRUM_API_PASSWORD` are your credentials associated with the Spectrum Metrics Django app, and `DEVICE_SERIAL_NUMBER` and `DEVICE_MODEL` correspond to the serial number and model of the Pulse Tracer device running the code

## Database Objects
Ensure you have created the following objects in the Spectrum Metrics web app before you run the pipeline:

**Device** - a device object with the same serial number and model as the Pulse Tracer device

**Health Care Provider** - a health care provider to be associated with the patient

**Patient** - a patient associated with the above health care provider and device



## Running the Preprocessing Pipeline

