from constants import TENANT_NAME
from init import create_table, create_dataset
from lib.util import bigquery_connection

from google.cloud import bigquery


def main():
    client = bigquery_connection()
    create_dataset(client)
    dataset = bigquery.DatasetReference(client.project, TENANT_NAME)
    create_table(client, dataset, 'shopify_products', 'schema/product.json')
    create_table(client, dataset, 'shopify_product_variants', 'schema/product_variant.json')
    create_table(client, dataset, 'shopify_orders', 'schema/order.json')
    create_table(client, dataset, 'shopify_customer_visits', 'schema/customer_visit.json')
    create_table(client, dataset, 'shopify_discount_applications', 'schema/discount_application.json')
    create_table(client, dataset, 'shopify_customers', 'schema/customers.json')

if __name__ == "__main__":
    main()
