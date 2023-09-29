import json
import os
from google.cloud import bigquery
from google.cloud.bigquery import Dataset, SchemaField
from google.cloud.bigquery.client import Client
from dotenv import load_dotenv

from constants import TENANT_NAME
from get_data import get_products, get_customers, get_orders
from lib.util import bigquery_connection

load_dotenv()


def main():
    client = bigquery_connection()
    create_dataset(client)
    dataset_ref = bigquery.DatasetReference(client.project, TENANT_NAME)
    # init_products(client, dataset_ref)
    # init_customers(client, dataset_ref)
    init_orders(client, dataset_ref)


def init_products(client, dataset):
    create_table(client, dataset, 'shopify_products', 'schema/product.json')
    create_table(client, dataset, 'shopify_product_variants', 'schema/product_variant.json')
    get_products(dataset, client)


def init_orders(client, dataset):
    create_table(client, dataset, 'shopify_orders', 'schema/order.json')
    create_table(client, dataset, 'shopify_customer_visits', 'schema/customer_visit.json')
    create_table(client, dataset, 'shopify_discount_applications', 'schema/discount_application.json')

    get_orders(dataset, client)


def init_customers(client, dataset):
    create_table(client, dataset, 'shopify_customers', 'schema/customers.json')
    get_customers(dataset, client)


def create_dataset(client: Client):
    # Construct a BigQuery client object.
    try:
        # Send the dataset to the API for creation, with an explicit timeout.
        # Raises google.api_core.exceptions.Conflict if the Dataset already
        # exists within the project.
        # @todo remove `exists_ok` after testing is complete
        dataset = client.create_dataset(TENANT_NAME, timeout=30, exists_ok=True)
        print("Created dataset {}.{}".format(client.project, dataset.dataset_id))
        dataset.location = os.getenv('LOCATION')

    except Exception as e:
        print(f"Error: {str(e)}")


def create_table(client: Client, dataset: Dataset, table_name: str, schema_path: str):
    table_id = f"{dataset.project}.{dataset.dataset_id}.{table_name}"
    # Read the schema from the JSON file
    with open(schema_path, 'r') as file:
        schema_json = json.load(file)
        print(schema_json)
        schema = [SchemaField.from_api_repr(field) for field in schema_json]

    table = bigquery.Table(table_id, schema=schema)
    # Create the table in BigQuery
    try:
        client.create_table(table)
        print(f"Table {table_id} created successfully.")
    except Exception as e:
        print(f"Error creating table {table_id}: {e}")


if __name__ == "__main__":
    main()
