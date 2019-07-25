#This script import a JSON file into Azure SQL server

from azure.storage.blob import BlockBlobService, PublicAccess
import os
import json
import pyodbc

# connect to Azure
dsn = 'rpitestsqlserverdatasource' #Set up connection to an ODBC data soure-already set up on the current rpi

user = 'team2@capstonesfu'

password = '@ensc405'

database = 'mydb'

connString = 'DSN={0};UID={1};PWD={2};DATABASE={3};'.format(dsn,user,password,database)

conn = pyodbc.connect(connString) 
cursor = conn.cursor()


#Open and read JSON file

#Modify the datapath when using
file=os.path.abspath('/home/pi/Desktop/example_1.json')
json_data=open(file).read()
json_obj=json.loads(json_data)

#Parsing the JSON string
def validate_string(val):
   if val != None:
        if type(val) is int:
            #for x in val:
            #   print(x)
            return str(val).encode('utf-8')
        else:
            return val


# import json data to SQL insert
#here we are adding in 2 columns (id [int] , name [string])
for i, item in enumerate(json_obj):
    id_ = item.get("id",None)
    name = validate_string(item.get("name",None))

    cursor.execute("INSERT INTO dbo.testing(id,name) VALUES (?,?)", (id_,name))

#Commit the insertion 
conn.commit()
conn.close()
