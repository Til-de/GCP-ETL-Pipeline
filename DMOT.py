import os
import time
from abc import ABC, abstractmethod

import requests
from google.cloud import bigquery
from google.cloud.bigquery import Client, Dataset
from google.oauth2 import service_account


class Extractor(ABC):
    def __init__(self, project_id, shop_name, token, client=None):
        self.client = self._connect(token, project_id) if client is None else client
        self.dataset = self._get_dataset_reference()
        self.headers = {'X-Shopify-Access-Token': token, 'Content-Type': 'application/json'}
        self.shop_name = shop_name
        self.url = f"https://{shop_name}.myshopify.com/admin/api/{os.getenv('SHOP_API_VERSION')}/graphql.json"

    def set_dataset_reference(self, dataset_id):
        self.dataset = bigquery.DatasetReference(dataset_id)

    def create_dataset(self):
        # Construct a BigQuery client object.
        try:
            # Send the dataset to the API for creation, with an explicit timeout.
            # Raises google.api_core.exceptions.Conflict if the Dataset already
            # exists within the project.
            # @todo remove `exists_ok` after testing is complete
            dataset = self.client.create_dataset(self.shop_name, timeout=30)
            print("Created dataset {}.{}".format(self.client.project, dataset.dataset_id))
            dataset.location = os.getenv('LOCATION')
            return dataset

        except Exception as e:
            print(f"Error: {str(e)}")
    def _get_dataset_reference(self):
        return bigquery.DatasetReference(self.client.project)

    @abstractmethod
    def migrate(self):
        pass

    def _connect(self, token, project_id):
        credentials = service_account.Credentials.from_service_account_file(
            token, scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        client = bigquery.Client(project=project_id, credentials=credentials)

    @abstractmethod
    def get_data(self):
        pass

    @abstractmethod
    def save_data(self):
        pass

    def insert_json_rows(self, table_ref, rows):
        """Uploads a batch of rows to a specified table and returns any errors encountered"""
        try:
            print(f"uploading {len(rows)} records to {table_ref.dataset_id}.{table_ref.table_id} ...")
            errors = self.client.insert_rows_json(table_ref, rows)
            if errors:
                print(f'Encountered errors while inserting rows to {table_ref.table_id}: {errors}')
            else:
                print(f"{len(rows)} successfully uploaded to {table_ref.dataset_id}.{table_ref.table_id}")
        except Exception as e:
            print(f'Encountered errors while inserting rows to {table_ref.table_id}: {errors}')


    def get_table_ref(self, table_id):
        return bigquery.TableReference(self.dataset, table_id)



    def create_table(client: Client, dataset: Dataset, table_name: str, schema_path: str):
        table_id = f"{dataset.project}.{dataset.dataset_id}.{table_name}"
        # Read the schema from the JSON file
        with open(schema_path, 'r') as file:
            schema_json = json.load(file)
            schema = [SchemaField.from_api_repr(field) for field in schema_json]

        table = bigquery.Table(table_id, schema=schema)
        # Create the table in BigQuery
        try:
            client.create_table(table)
            print(f"Table {table_id} created successfully.")
        except Exception as e:
            print(f"Error creating table {table_id}: {e}")
    def _get_bulk_operation_run_query_url(self, query):
        response = requests.post(url=self.url, headers=self.headers, json={
            "query": self.BULK_OPERATION_RUN_QUERY,
            "variables": {
                "subquery": query
            }
        })
        print(f"response {response.status_code} for {self.name} BulkOperationRunQuery")

        # @TODO add error handling
        if response.status_code == 200:
            while True:
                op_state = requests.post(url=self.url, headers=self.headers, json={
                    "query": self.BULK_OPERATION_STATUS,
                })
                json_data = op_state.json()
                status = json_data['data']['node']['status']
                errorcode = json_data['data']['node']['errorCode']
                if errorcode is not None:
                    print(f"Shopify BulkOperationRunQuery error:{errorcode}")
                if status == "COMPLETED":
                    url = json_data['data']['node']['url']
                    return url
                time.sleep(self.POLL_INTERVAL_SECONDS)
        else:
            print("Query failed to run by returning code of {}.".format(response.status_code))
