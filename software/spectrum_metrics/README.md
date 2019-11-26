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
```
DATABASES = {
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

Finally, make sure the `PULSE_TRACER_SECRET_KEY` variable is set in your environment, as well as `SPECTRUM_API_USERNAME` and `SPECTRUM_API_PASSWORD`, which are the credentials you use to login to the Spectrum Metrics web app. 

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
and navigate to `127.0.0.0:8000` in your web browser

To run on your localhost with a specific port, use
```
python3 manage.py runserver localhost:PORT_NUMBER
```
and navigate to `127.0.0.0:PORT_NUMBER` in your web browser

# Installing the Spectrum Metrics Web App on an Azure VM
If you choose to run the Spectrum Metrics web app on an Azure VM, you can use a DNS to access the web app from any machine. 

## Setting up the Azure VM
Go to portal and follow the instructions to create an Azure VM. Select your preferred VM size, and make sure to allow SSH, HTTP, and HTTPS access (ports 22, 80, and 443, respectively). Once the resource has been deployed, navigate to its overview and configure a DNS. Choose your own unique DNS name, this will be the first part of the URL for your web application. 

Once the VM is all set up, take note of the IP address located on overview page. You can SSH into the VM using this IP and the username you used to create the VM as follows:
```
ssh user@ip_address
```
You will then be prompted to enter the password associated with this username. 


## Installing Spectrum Metrics Dependencies
Once you have successfully logged into the VM, you can now install the dependencies required to run the web application. 

First, clone the repo if you haven't done so already 
```
git clone https://csil-git1.cs.surrey.sfu.ca/capstone-1194-group-2/capstone.git
```

You will then need to install some dependencies on the VM iteself. This must be done before you install anything from `requirements.txt`
```
sudo apt-get update
sudo apt-get install build-essential
sudo apt-get install unixodbc unixodbc-dev
sudo apt-get install python3-dev
```

After this, you can install the requirements using
```
pip install -r requirements.txt
```

The next step will be to install the OBDC driver 17 for SQL server, found at [this link](https://www.microsoft.com/en-us/download/details.aspx?id=56567). Follow the installation instructions, whether you are running Windows, macOS, or Linux. Because the OS for the VM will most likely be Ubuntu, you should not have to download anything directly from this link. 

The final step is to install `pyodbc` to allow Python to talk to the Azure database. On Ubuntu this needs to be installed using the wheel file. To do so, download the file [here](https://pypi.org/project/django-pyodbc-azure/#files) on your local machine. Copy the file from your local to the Azure VM using
```
rsync -avPL django_pyodbc_azure-2.1.0.0-py3-none-any.whl username@ip_address:/home/username/
```
Then, navigate to the file and install it with 
```
pip install django_pyodbc_azure-2.1.0.0-py3-none-any.whl
```

You will then need to modify `spectrum_metrics/settings.py` to ensure the correct database is being used. You will most likely be using the Azure cloud database when using a VM, therefore ensure the database is set to
```
DATABASES = {
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

Finally, make sure the `PULSE_TRACER_SECRET_KEY` variable is set in your environment, as well as `SPECTRUM_API_USERNAME` and `SPECTRUM_API_PASSWORD`, which are the credentials you use to login to the Spectrum Metrics web app.

If you're using a DNS, you will need to make sure the DNS name is added to the `ALLOWED_HOSTS` list in `spectrum_metrics/settings.py`

## Running the Spectrum Metrics App on an Azure VM
Once the requirements and drivers have been installed, you will need to make and apply the migrations to the database
```
python3 manage.py makemigrations
python3 manage.py migrate
```

Now you should be able to successfully run the web application. 

If you want to run on your localhost, use
```
python3 manage.py runserver 
```
and navigate to `127.0.0.0:8000` in your web browser

If you want to run on your localhost with a specific port, use
```
python3 manage.py runserver localhost:PORT_NUMBER
```
and navigate to `127.0.0.0:PORT_NUMBER` in your web browser

If you want to run on your configured DNS, use
```
python3 manage.py runserver 0.0.0.0:PORT_NUMBER
```
and navigate to `http://dns_name:PORT_NUMBER` in your web browser

