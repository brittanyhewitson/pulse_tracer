# Spectrum Metrics
## Overview of the Spectrum Metrics Web Application
Spectrum Metrics is a Django-built web application that provides an interface for both patients and health care providers to interact with the data collected on each patient by their associated Pulse Tracer device. The website allows for two different types of users, either a Patient or a Health Care Provider. Patients will select which health care providers are allowed to view their data, and both have access to the heart rate and respiratory rate data calculated for each patient. If you want more information regarding how the heart rate and respiratory rates are calculated from the raw video data, refer to the [analysis](https://csil-git1.cs.surrey.sfu.ca/capstone-1194-group-2/capstone/tree/master/software/analysis) and the [data stream ](https://csil-git1.cs.surrey.sfu.ca/capstone-1194-group-2/capstone/tree/master/software/data_stream) directories.

The Spectrum Metrics web app has the following tables and columns:

### Device
| Column | Description |
| :----: | ----------- |
| `device_model` | The model for the associated Pulse Tracer device |
| `serial_number` | The unique serial number for each Pulse Tracer device |

### ROI
| Column | Description |
| :----: | ----------- |
| `location_id` | The location for which each ROI was extracted from. Refer to the [location ID choices](https://csil-git1.cs.surrey.sfu.ca/capstone-1194-group-2/capstone/blob/master/software/spectrum_metrics/pulse_tracer/models.py#L26) for specific details regarding which location IDs exist |
| `batch_id` | The ID of the batch each ROI belongs to. There are typically 900 ROIs in each batch, representing a total of 30 seconds of data |
| `red_data` | The ROI data for the red channel represented by a 2-D matrix |
| ` greed_data` | The ROI data for the green channel represented by a 2-D matrix |
| `blue_data` | The ROI data for the blue channel represented by a 2-D matrix |
| `collection_time` | The specific time at which each ROI was calculated. This provides a means of sorting the data in each batch |
| `hr_analyzed` | A boolean representing whether the ROI has been used to determine a heart rate |
| `rr_analyzed` | A boolean representing whether the ROI has been used to determine a respiratory rate |
| `analysis_in_progress` | A boolean representing whether the ROI is currently being analyzed for HR or RR |
| `device` | A foreign key to the device from which this ROI was collected from |

### User
| Column | Description |
| :----: | ----------- |
| `is_patient` | A boolean representing whether the user is a patient or not |
| `is_health_care` | A boolean representing whether the user is a health care provider or not |

### Health Care Provider
| Column | Description |
| :----: | ----------- |
| `user` | Foreign key to the Django User |
| `role` | The professional role for the health care provider. Refer to the [role choices](https://csil-git1.cs.surrey.sfu.ca/capstone-1194-group-2/capstone/blob/master/software/spectrum_metrics/pulse_tracer/models.py#L158) for specific details regarding which roles exist |

### Patient
| Column | Description |
| :----: | ----------- |
| `user`| Foreign key to the Django User |
| `birth_date` | Date of birth for the patient |
| `gender` | Gender of the patient |
| `weight` | Weight of the patient in kg |
| `height` | Height of the patient in cm |
|`health_conditions` | Any pre-existing health conditions the patient has been diagnosed with |
| `device` | Foreign key to the device which belongs to the patient |
| `health_care_provider` | A list of foreign keys to the health care providers which the patient has selected to have access to their data |

### Heart Rate
| Column | Description |
| :----: | ----------- |
| `heart_rate` | A floating point number representing the calculated heart rate value for the associated ROIs |
| `data` | The extracted HR waveform for the associated ROIs |
| `analyzed_time` | The time at which the associated ROIs were analyzed to produce a heart rate value |
| `patient` | The patient associated with the ROIs |
| `rois` | The ROIs associated with the calculated HR |

### Respiratory Rate
| Column | Description |
| :----: | ----------- |
| `respiratory_rate` | A floating point number representing the calculated respiratory rate value for the associated ROIs |
| `data` | The extracted HR waveform for the associated ROIs |
| `analyzed_time` | The time at which the associated ROIs were analyzed to produce a respiratory rate value |
| `patient` | The patient associated with the ROIs |
| `rois` | The ROIs associated with the calculated RR |


## Installing Spectrum Metrics on your local machine
If you haven't done so already, clone the repo on your machine 
```
git clone https://csil-git1.cs.surrey.sfu.ca/capstone-1194-group-2/capstone.git
```

Next, navigate into the `software/spectrum_metrics` directory and install the requirements
```
cd software/spectrum_metrics
pip install -r requirements.txt
```

Depending on whether you choose to use a local PostgreSQL database or an Azure database, you will need to set up your database and modify `spectrum_metrics/settings.py` accordingly. 

If you choose to use a PostgreSQL database, modify the `DATABASES` dictionary in `settings.py` to be:
```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': YOUR_DATABASE_NAME,
        'USER': YOUR_DATABASE_USER,
        'PASSWORD': YOUR_DATABASE_PASSWORD,
        'HOST': 'localhost',
        'PORT': '5432',
    },
}
```
filling in the values for your database name, your database user, and your database password. 

If you choose to use an Azure cloud database, modify the `DATABASES` dictionary in `settings.py` to be:
```DATABASES = {
    'default': {
        'ENGINE': 'sql_server.pyodbc',
        'HOST': YOUR_HOST,
        'PORT': '1433',
        'NAME': YOUR_DATABASE_NAME,
        'USER': 'YOUR_DATABASE_USER,
        'PASSWORD': YOUR_DATABASE_PASSWORD,
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
            'unicode_results': True,
        },
    },
}
```
filling in the values for your host, database name, your database user, and your database password. You will also need to install the OBDC driver 17 for SQL server, found at [this link](https://www.microsoft.com/en-us/download/details.aspx?id=56567). Follow the installation instructions, whether you are running Windows, macOS, or Linux. 



## Running the Spectrum Metrics Web App on your local machine 
Once the requirements and drivers have been installed, you will need to make and apply the migrations to the database
```
python3 manage.py makemigrations
python3 manage.py migrate
```

After this, you are ready to run the web application. To run it on your localhost, use
```
python3 manage.py runserver
```

To run on your localhost with a specific port, use
```
python3 manage.py runserver localhost:PORT_NUMBER
```

If you are running on an Azure VM and you want to use your specific DNS, use
```
python3 manage.py runserver DNS_NAME:PORT_NUMBER
```

