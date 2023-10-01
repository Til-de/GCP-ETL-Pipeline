import os
from dotenv import load_dotenv

load_dotenv()

PROJECT_ID = os.getenv('GCP_PROJECT_ID') if os.getenv('GCP_PROJECT_ID') is not None else "<insert_project_id>"
KEY_PATH = os.getenv('SERVICE_ACCOUNT_KEY_PATH') if os.getenv(
    'SERVICE_ACCOUNT_KEY_PATH') is not None else "<INSERT_KEY_PATH>"
GRAPH_ENDPOINT = f"https://{os.getenv('SHOP_DOMAIN')}/admin/api/{os.getenv('SHOP_API_VERSION')}/graphql.json"
TENANT_NAME = 'no_maintenance'
DATASET_ID = f"{PROJECT_ID}.{TENANT_NAME}"
SHOPIFY_ACCESS_TOKEN = os.getenv('SHOPIFY_ACCESS_TOKEN')


SHOP_TABLES = {
    "ORDERS": "shopify_orders",
    "CUSTOMERS": "shopify_customers",
    "CUSTOMER_VISITS": "shopify_customer_visits",
    "PRODUCTS": "shopify_products",
    "PRODUCT_VARIANTS": "shopify_product_variants",
    "SHOPIFY_DISCOUNT_APPLICATIONS": "shopify_discount_applications"
}