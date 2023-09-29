import json
import os
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
    # requests lib is used to send the query
    print("response status code: ", response.status_code)

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
            print(errorcode)
            if status == "COMPLETED":
                url = json_data['data']['node']['url']
                return url
            time.sleep(30)
    else:
        print("Query failed to run by returning code of {}.".format(response.status_code))


def upload_batch(client, table_ref, batch):
    """Uploads a batch of rows to a specified table and returns any errors encountered"""
    errors = client.insert_rows_json(table_ref, batch)
    if errors:
        print(f'Encountered errors while inserting rows to {table_ref.table_id}: {errors}')
    return errors


def get_products(dataset_ref, client=bigquery_connection()):
    url = get_bulk_data_url(GET_ALL_PRODUCTS_QUERY)
    bulk_op_res = urlopen(url)
    json_data = bulk_op_res.read().decode('utf-8', 'replace')

    products = []
    variants = []
    products_table_ref = bigquery.TableReference(dataset_ref, f"shopify_products")
    variants_table_ref = bigquery.TableReference(dataset_ref, f"shopify_product_variants")

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
    table_ref = bigquery.TableReference(dataset_ref, f"shopify_customers")

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



def get_orders(dataset_ref, client):
    # url = get_bulk_data_url(GET_ALL_ORDERS_QUERY)
    url = "https://storage.googleapis.com/shopify-tiers-assets-prod-us-east1/7eypgm4ib5cdq8zm5afq79pyd6ak?GoogleAccessId=assets-us-prod%40shopify-tiers.iam.gserviceaccount.com&Expires=1696607847&Signature=iW8FUEYjQ32dYOFVblETGr%2BzvXW57pgInmputJ4VOL0c72NfF%2FL4QXiH3wfYkMiBET5lNzId1Kb47YBWON3KkgMm67ie%2F0kzCMVpDdY7WN%2BnSU8rOYP%2BGuofg%2FwH7pqnuKOZoxHkSlM%2BpD8IeG6wmit0YyVMCzNs844Hgc%2FkZeJ6Luk7kP3wv8SZifRkVXtXXexV5MGjNbyzoLBRvUpPTUzbamJzOvDK0Wwo5a0yG2IcL31reTK5mUmJKJHM5Q%2Bi5lb%2FspKzOBav9xBRI17qCAfbZxZLNTTVh6kPKgROQ%2FyQrEOfO%2FuHAX29lCfThtVJ1fYeq7IqDtKPG4k3a0Iakw%3D%3D&response-content-disposition=attachment%3B+filename%3D%22bulk-3658532192494.jsonl%22%3B+filename%2A%3DUTF-8%27%27bulk-3658532192494.jsonl&response-content-type=application%2Fjsonl"
    bulk_op_res = urlopen(url)
    json_data = bulk_op_res.read().decode('utf-8', 'replace')

    orders = []
    customer_visits = []
    discount_applications = []
    orders_table = bigquery.TableReference(dataset_ref, f"shopify_orders")
    customer_visits = bigquery.TableReference(dataset_ref, f"shopify_customer_visits")
    orders_table = bigquery.TableReference(dataset_ref, f"shopify_discount_application")


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
