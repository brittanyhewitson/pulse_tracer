import pyodbc

server = 'capstonesfu.database.windows.net'
database = 'spectrum_metrics'
username = 'team2@capstonesfu'
password = '@ensc405'
driver= '{ODBC Driver 17 for SQL Server}'

# Executes SQL on the following tables
tables = ['pulse_tracer_device','pulse_tracer_healthcare','pulse_tracer_heartrate','pulse_tracer_patient','pulse_tracer_patient_health_care_provider','pulse_tracer_respiratoryrate','pulse_tracer_roi']

# Connect to db
connection = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password)
cursor = connection.cursor()

# Generates DELETE FROM commands
queries = [('DELETE FROM dbo.'+table) for table in tables]

# Executes commands on db
for query in queries:
	cursor.execute(query)

connection.commit()