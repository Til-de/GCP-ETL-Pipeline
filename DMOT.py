import json
import sys
from abc import ABC, abstractmethod
from typing import Union, List

from google.cloud import bigquery
from google.cloud.bigquery import Client, SchemaField
from google.cloud.exceptions import NotFound
from google.oauth2 import service_account

from errors import DatasetExistsError
from util import get_file_from_project_root


class TableInfo:
    def __init__(self, key: Union[str, List[str]], name: str, schema: str):
        # Ensure key is always a list
        self.key = key if isinstance(key, list) else [key]
        self.name = name
        self.schema = schema


class DataModel(ABC):
    def __init__(self, project_id, bq_token, location, tenant, client=None):
        self.project_id = project_id
        self.client = self._connect(bq_token, self.project_id) if client is None else client
        self.tenant = tenant
        self.location = location
        print(f"tenant: {self.tenant}")
        self.dataset_ref = self._set_dataset_reference(tenant)

    def _set_dataset_reference(self, dataset_id: str):
        return bigquery.DatasetReference(self.project_id, dataset_id)

    def has_dataset(self):
        try:
            self.client.get_dataset(self.dataset_ref.dataset_id)  # Make an API request.
            print("Dataset {} already exists".format(self.dataset_ref.dataset_id))
            return True
        except NotFound:
            return False

    def create_dataset(self, dataset_id=None):
        # Construct a BigQuery client object.
        try:
            d_id = self.dataset_ref.dataset_id if dataset_id is None else dataset_id
            # Send the dataset to the API for creation, with an explicit timeout.
            # Raises google.api_core.exceptions.Conflict if the Dataset already
            # exists within the project.
            dataset = self.client.create_dataset(d_id, timeout=30)
            self.dataset_ref = dataset
            print("Created dataset {}.{}".format(self.dataset_ref.project, self.dataset_ref.dataset_id))
            dataset.location = self.location
            return dataset
        except DatasetExistsError as e:
            print(e)

    @abstractmethod
    def migrate(self, tables: List[TableInfo]):
        pass

    def _connect(self, token, project_id) -> Client:
        credentials = service_account.Credentials.from_service_account_file(
            get_file_from_project_root(token), scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        client = bigquery.Client(project=project_id, credentials=credentials)
        return client

    @abstractmethod
    def get_data(self, query):
        pass

    @abstractmethod
    def save_data(self, data, table):
        pass

    def insert_json_rows(self, table_ref, rows):
        """Uploads a batch of rows to a specified table and returns any errors encountered"""
        try:
            print(f"uploading {len(rows)} records to {table_ref.dataset_id}.{table_ref.table_id} ...")
            errors = self.client.insert_rows_json(table_ref, rows)
            if errors:
                raise Exception(f"Encountered errors while inserting rows to {table_ref.table_id}: {errors}")
            else:
                print(f"{len(rows)} successfully uploaded to {table_ref.dataset_id}.{table_ref.table_id}")
        except Exception as e:
            print(f'Encountered errors while inserting rows to {table_ref.table_id}: {errors}')

    def get_table_ref(self, table_id):
        return bigquery.TableReference(self.dataset_ref, table_id)

    def create_table(self, table_name: str, schema_path: str):
        table_id = f"{self.dataset_ref.project}.{self.dataset_ref.dataset_id}.{table_name}"
        # Read the schema from the JSON file
        with open(schema_path, 'r') as file:
            schema_json = json.load(file)
            schema = [SchemaField.from_api_repr(field) for field in schema_json]

        table = bigquery.Table(table_id, schema=schema)
        # Create the table in BigQuery
        try:
            self.client.create_table(table, True)
            print(f"Table {table_id} created successfully.")
        except Exception as e:
            print(f"Error creating table {table_id}: {e}")
            sys.exit(1)


class Transformer(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def process_batched_data(self, data):
        pass
