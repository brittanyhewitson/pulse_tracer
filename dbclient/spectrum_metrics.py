import os
import sys
import json
import coreapi
import requests
import logging

from coreapi.codecs import JSONCodec, TextCodec
from openapi_codec import OpenAPICodec
import datetime

SPECTRUM_METRICS_API_URL = os.environ.get("SPECTRUM_API_URL", "http://127.0.0.1:8000/api/")

# Set up logging
LOGGING_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(format=LOGGING_FORMAT, stream=sys.stderr, level=logging.INFO)


class NotImplementedError(Exception):
    pass


class NotFoundError(Exception):
    pass


class PostError(Exception):
    def __init__(self, post_type=None, response=None, msg=None, **data):
        if msg:
            self.msg = msg
        else:
            table = data["table"].strip("s")
            id = data["id"]
            self.msg = f"Could not {post_type} {table} with id {id}\
            \nError code: {response.status_code}\nMessage: {response.text}"

    def __str__(self):
        return self.msg


class BadInput(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class InputWarning(UserWarning):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class SpectrumApi(object):
    def __init__(self):
        self.username = os.environ.get("SPECTRUM_API_USERNAME")
        self.password = os.environ.get("SPECTRUM_API_PASSWORD")
        self.api_url = SPECTRUM_METRICS_API_URL
        self.swagger_url = self.api_url + "swagger"
        self.pagination_parameter_names = ("page")

        # Define a session and provide authentication
        self.session = requests.Session()
        if self.username is not None and self.password is not None:
            self.session.auth = (self.username, self.password)
        else:
            raise Exception("Please set your authentication credentials")

        # Set up the session to send JSON
        self.session.headers.update({"content-type": "application/json"})
        
        # Set up coreapi to generate schema
        auth = coreapi.auth.BasicAuthentication(
            username=self.username, 
            password=self.password
        )
        decoders = [OpenAPICodec(), JSONCodec(), TextCodec()]
        self.coreapi_client = coreapi.Client(auth=auth, decoders=decoders)
        self.coreapi_schema = self.coreapi_client.get(self.swagger_url)
        
    def list_resources(self, table, **fields):
        params = {}
        # Get only the fields in the "list" fields
        for field in self.coreapi_schema[table]["list"].fields:
            if field.name in fields:
                params[field.name] = fields[field.name]

        params["page"] = 1

        # Iterate through pages of the API
        while True:
            list_results = self.coreapi_client.action(
                self.coreapi_schema, 
                [table, "list"],
                params=params
            )
            if list_results["count"] == 0:
                raise NotFoundError

            for result in list_results["results"]:
                yield result

            if list_results.get("next") is None:
                break

            params["page"] += 1

    def get(self, table, **fields):
        list_results = self.list_resources(
            table, 
            **fields
        )
        
        try:
            result = next(list_results)
        except StopIteration:
            raise NotFoundError

        try:
            result = next(list_results)
            raise Exception(f"More than one result for {table} with {fields}")
        except StopIteration:
            pass
            
        return result
    
    def create(self, table, **fields):
        # Try getting the object first
        try:
            new_object = self.get(
                table, 
                **fields
            )
            id = new_object["id"]
            raise PostError(msg=f"Cannot create {table}.\
                \nObject already exists with ID {id}")
        except NotFoundError:
            pass

        new_object = self.coreapi_client.action(
            self.coreapi_schema, 
            [table, "create"],
            params=fields
        )

        id = new_object["id"]
        logging.info(f"Successfully created {table} with ID {id}")
        return new_object
    
    def update(self, table, id, **fields):
        if id is None:
            raise BadInput("Please specify an ID for the object you are editing")
        
        # Get the object first to see if it exists
        try:
            self.get(table, id=id)
        except NotFoundError:
            table = table.split("s")
            logging.warning(f"{table} with ID {id} does not exist. Will not update")
            return

        url_contents = [self.api_url, table, str(id)]
        patch_url = "/".join(s.strip("/") for s in url_contents)

        response = self.session.patch(
            patch_url + "/", 
            data=json.dumps(fields)
        )

        if not response.ok:
            raise PostError(
                "update", 
                response, 
                id=id,
                table=table, 
                **fields
            )

        table = table.strip("s")
        logging.info(f"Successfully updated {table} with ID {id}")
        return response.json()

    def delete(self, table, id): 
        if id is None:
            raise BadInput("Please specify an ID for the object you are deleting")

        # Get the object first to see if it exists
        try:
            self.get(table, id=id)
        except NotFoundError:
            table = table.split("s")
            logging.warning(f"{table} with ID {id} does not exist. Will not delete")
            return

        url_contents = [self.api_url, table, str(id)]
        delete_url = "/".join(s.strip("/") for s in url_contents)

        response = self.session.delete(
            delete_url
        )

        if not response.ok:
            raise PostError(
                "delete", 
                response, 
                id=id,
                table=table, 
            )
        table = table.strip("s")
        logging.info(f"Successfully deleted {table} with ID {id}")

    def get_or_create(self, table, **fields):
        try:
            return self.get(table, **fields)
        except NotFoundError:
            return self.create(table, **fields)

    def create_patient(self):
        raise NotImplementedError

    def create_device(self):
        raise NotImplementedError

    def create_roi(self):
        raise NotImplementedError

    def create_health_care(self):
        raise NotImplementedError

    def create_hr(self):
        raise NotImplementedError

    def create_rr(self):
        raise NotImplementedError

