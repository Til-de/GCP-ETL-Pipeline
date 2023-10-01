import json
import time
from urllib.request import urlopen

import requests
from google.cloud import bigquery

from constants import GRAPH_ENDPOINT, SHOPIFY_ACCESS_TOKEN
from lib.util import bigquery_connection
from query import BULK_OPERATION_STATUS_BY_ID, GET_ALL_PRODUCTS_QUERY, BULK_OPERATION_RUN_QUERY, \
    GET_ALL_CUSTOMERS_QUERY, GET_ALL_ORDERS_QUERY


def get_bulk_data_url(query):
    headers = {'X-Shopify-Access-Token': SHOPIFY_ACCESS_TOKEN, 'Content-Type': 'application/json'}
    response = requests.post(url=GRAPH_ENDPOINT, headers=headers, json={
        "query": BULK_OPERATION_RUN_QUERY,
        "variables": {
            "subquery": query
        }
    })
    print("response status code for BulkOperationRunQuery:", response.status_code)

    if response.status_code == 200:
        op_id = response.json()["data"]["bulkOperationRunQuery"]["bulkOperation"]["id"]
        while True:
            op_state = requests.post(url=GRAPH_ENDPOINT, headers=headers, json={
                "query": BULK_OPERATION_STATUS_BY_ID,
                "variables": {
                    "id": op_id
                }})
            json_data = op_state.json()
            status = json_data['data']['node']['status']
            errorcode = json_data['data']['node']['errorCode']
            if errorcode is not None:
                print(f"Shopify BulkOperationRunQuery error:{errorcode}")
            if status == "COMPLETED":
                url = json_data['data']['node']['url']
                print(f"BulkOperationRunQuery complete. See,\n {url}")
                return url
            time.sleep(30)
    else:
        print("Query failed to run by returning code of {}.".format(response.status_code))


def upload_batch(client, table_ref, batch):
    print(f"uploading {len(batch)} records to {table_ref.dataset_id}.{table_ref.table_id} ...")
    """Uploads a batch of rows to a specified table and returns any errors encountered"""
    errors = client.insert_rows_json(table_ref, batch)
    if errors:
        print(f'Encountered errors while inserting rows to {table_ref.table_id}: {errors}')
    else:
        print(f"{len(batch)} successfully uploaded to {table_ref.dataset_id}.{table_ref.table_id}")
    return errors


def get_products(dataset_ref, client=bigquery_connection()):
    url = get_bulk_data_url(GET_ALL_PRODUCTS_QUERY)
    bulk_op_res = urlopen(url)
    json_data = bulk_op_res.read().decode('utf-8', 'replace')

    products = []
    variants = []
    products_table_ref = bigquery.TableReference(dataset_ref, "shopify_products")
    variants_table_ref = bigquery.TableReference(dataset_ref, "shopify_product_variants")

    # Since Shopify's bulk operation flattens the GQL response, there are two types of objects:
    # product & products variants
    # For every product that contains a variant, the JSONL file will add the product first,
    # then each of its variants will be added in subsequent lines
    tmp_product_ref = None
    for line in json_data.splitlines():
        row_json = json.loads(line)

        # Determine the appropriate batch and table_ref based on the presence of '__parentId'
        if '__parentId' in row_json:
            batch = variants
            if tmp_product_ref:
                tmp_product_ref["variants"].append(row_json["id"])
        else:
            batch = products
            tmp_product_ref = row_json
            tmp_product_ref["variants"] = []

        # Add the row to the appropriate batch
        batch.append(row_json)

    if products:
        upload_batch(client, products_table_ref, products)

    if variants:
        upload_batch(client, variants_table_ref, variants)


def get_customers(dataset_ref, client=bigquery_connection()):
    url = get_bulk_data_url(GET_ALL_CUSTOMERS_QUERY)
    table_ref = bigquery.TableReference(dataset_ref, "shopify_customers")

    bulk_op_res = urlopen(url)
    json_data = bulk_op_res.read().decode('utf-8', 'replace')

    batch_size = 5000
    batch = []
    # Stream the data directly to BigQuery in batches
    for line in json_data.splitlines():
        row_json = json.loads(line)
        batch.append(row_json)
        # Check if the batch size has reached the defined batch_size and upload if necessary
        if len(batch) >= batch_size:
            upload_batch(client, table_ref, batch)
            # Clear the batch after uploading
            batch.clear()

    # Upload any remaining rows in the batches
    upload_batch(client, table_ref, batch)


class TxBatch:
    def __init__(self, table_ref, batch_size=1000):
        self.contents = []
        self.table_ref = table_ref
        self.batch_size = batch_size


def unpack_nested_id(row: object, prop):
    if row[prop]:
        id = row[prop]["id"]
        row[prop] = id


def unpack_money_v2(row:dict, prop:str):
    if row[prop]:
        if row[prop]["shopMoney"]:
            row[prop] = row[prop]["shopMoney"]["amount"]
        elif row[prop]["presentmentMoney"]:
            row[prop] = row[prop]["presentmentMoney"]["amount"]


def get_orders(dataset_ref, client):
    # url = get_bulk_data_url(GET_ALL_ORDERS_QUERY)
    url = "https://storage.googleapis.com/shopify-tiers-assets-prod-us-east1/9hct4202judli655b0owhyaecsaz?GoogleAccessId=assets-us-prod%40shopify-tiers.iam.gserviceaccount.com&Expires=1696736254&Signature=AxWAWscYJT%2B3TsYuKWUHv4OQfSBK0pUVucus%2Bl6uisloIV5lTC0vh89F%2FKyo3jEHDrW7ZrlQN%2ByJ115xCOOasG0GfHkU7suDZiOPkLa09JSa1aIbSDW%2FvU%2BlfXIFVoKoY5uWC6VDoUEZ%2FsVKtgzhwE1j6vCUnHnqXgwzY3YZ2NqrKi%2BL1bwzmUaom3BJpl%2F4NN%2BW%2FRvOWr9KPso%2BXqTCNIx93n7PbMfTc%2FHqV4lwmfpoD6%2B3nhmVDlsN1rt8yTXMldH2N92C0ce6Fk%2FGzobqnq7vQxrqD5eTr30bqIuEfQRSO%2FMvhhsOZBvrj8VibpIikv2Q1TWuX7bf0q4djQwSqg%3D%3D&response-content-disposition=attachment%3B+filename%3D%22bulk-3663370420462.jsonl%22%3B+filename%2A%3DUTF-8%27%27bulk-3663370420462.jsonl&response-content-type=application%2Fjsonl"

    bulk_op_res = urlopen(url)
    json_data = bulk_op_res.read().decode('utf-8', 'replace')

    orders = TxBatch(bigquery.TableReference(dataset_ref, "shopify_orders"))
    customer_visits = TxBatch(bigquery.TableReference(dataset_ref, "shopify_customer_visits"))
    discount_applications = TxBatch(bigquery.TableReference(dataset_ref, "shopify_discount_applications"))
    for line in json_data.splitlines():
        row = json.loads(line)

        # Determine the appropriate batch and table_ref based on the presence of '__parentId'
        match row["__typename"]:
            case "Order":
                batch = orders
                unpack_nested_id(row, "app")
                unpack_nested_id(row, "customer")
                unpack_money_v2(row, "subtotalPriceSet")
                unpack_money_v2(row, "totalPriceSet")
                unpack_money_v2(row, "totalDiscountsSet")
                unpack_money_v2(row, "totalRefundedSet")
                for line in row["taxLines"]:
                    unpack_money_v2(line, "priceSet")
            case "CustomerVisit":
                batch = customer_visits
            case "DiscountCodeApplication" | "ManualDiscountApplication" | "AutomaticDiscountApplication":
                batch = discount_applications
            case _:
                print(f"no routine found in get_orders() to handle the following type:: {row['__typename']}")
                print(row)
        del row["__typename"]
        batch.contents.append(row)
        if len(batch.contents) >= batch.batch_size:
            upload_batch(client, batch.table_ref, batch.contents)
            # Clear the batch after uploading
            batch.contents.clear()
    for remaining in [orders, customer_visits, discount_applications]:
        if remaining.contents:
            upload_batch(client, remaining.table_ref, remaining.contents)
