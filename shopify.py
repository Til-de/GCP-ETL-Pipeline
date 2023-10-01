import json
import os
import time
from abc import ABC, abstractmethod
from typing import Type

import requests
from dotenv import load_dotenv
from google.cloud.bigquery import SchemaField
from google.oauth2 import service_account
from google.cloud import bigquery

from constants import SHOP_TABLES
load_dotenv()


class Channel(ABC):
    def  __init__(self, name, token, url, table_ref):
        self.name = name
        self.url = url
        self.headers = {'X-Shopify-Access-Token': token, 'Content-Type': 'application/json'}
        self.table_ref = table_ref

    @abstractmethod
    def extract(self, url):
        pass
    @abstractmethod
    def transform(self):
        pass

    def load(client, table_ref, batch):
        print(f"uploading {len(batch)} records to {table_ref.dataset_id}.{table_ref.table_id} ...")
        """Uploads a batch of rows to a specified table and returns any errors encountered"""
        errors = client.insert_rows_json(table_ref, batch)
        if errors:
            print(f'Encountered errors while inserting rows to {table_ref.table_id}: {errors}')
        else:
            print(f"{len(batch)} successfully uploaded to {table_ref.dataset_id}.{table_ref.table_id}")
        return errors
class ShopifyConnector:
    POLL_INTERVAL_SECONDS = 30
    def __init__(self, client, dataset, shop_name, token):
        self.client = client
        self.dataset = dataset
        self.headers = {'X-Shopify-Access-Token': token, 'Content-Type': 'application/json'}
        self.shop_name = shop_name
        self.url = f"https://{shop_name}.myshopify.com/admin/api/{os.getenv('SHOP_API_VERSION')}/graphql.json"


    def create_table(self, name, schema_path):
        table_id = f"{self.dataset.project}.{self.dataset.dataset_id}.{name}"
        # Read the schema from the JSON file
        with open(schema_path, 'r') as file:
            schema_json = json.load(file)
            schema = [SchemaField.from_api_repr(field) for field in schema_json]

        table = bigquery.Table(table_id, schema=schema)
        # Create the table in BigQuery
        try:
            self.client.create_table(table)
            print(f"Table {table_id} created successfully.")
        except Exception as e:
            print(f"Error creating table {table_id}: {e}")

    def get_dataset_reference(self, ):
        return bigquery.DatasetReference(self.client.project)

    def connect(self, token, project_id):
        credentials = service_account.Credentials.from_service_account_file(
            token, scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        bigquery.Client(project=project_id, credentials=credentials)

    def extract(self, channel: Type[Channel]):
        url = self.get_bulk_data_url(channel.)
    def get_bulk_data_url(self, query):
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

    def get_data(self):
    def init_migration(self):
        client.create_dataset(TENANT_NAME, timeout=30)
        self.create_table(SHOP_TABLES.ORDERS, 'schema/order.json')
        self.create_table(SHOP_TABLES.PRODUCTS, 'schema/product.json')
        self.create_table(SHOP_TABLES.PRODUCT_VARIANTS, 'schema/product_variant.json')
        self.create_table(SHOP_TABLES.CUSTOMER_VISIT, 'schema/customer_visit.json')
        self.create_table(SHOP_TABLES.DISCOUNT_APPLICATION, 'schema/discount_application.json')

    BULK_OPERATION_RUN_QUERY = '''
            mutation bulk_product_query($subquery: String!)  {
              bulkOperationRunQuery(
                query: $subquery
              ) {
                bulkOperation {
                  id
                  status
                }
                userErrors {
                  field
                  message
                }
              }
            }
        '''
    BULK_OPERATION_STATUS = """
        {
         currentBulkOperation {
           id
           status
           errorCode
           createdAt
           completedAt
           objectCount
           fileSize
           url
           partialDataUrl
         }
        }
        """

class Pipeline(ABC) {
    @abstractmethod
    def extract:
}