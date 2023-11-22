import json
from abc import abstractmethod
from typing import List
from urllib.request import urlopen

from DMOT import TableInfo
from query import GET_ALL_ORDERS_QUERY, GET_ALL_CUSTOMERS_QUERY, GET_ALL_PRODUCTS_QUERY
from shopify import ShopifyDataModel, ShopifyTransformer
from util import get_config, get_tenant_name, get_file_from_project_root


def main():
    config = get_config()
    extractor = ShopifyScheduledIngestionDataModel(
        project_id=config["BIGQUERY"]["PROJECT_NAME"],
        bq_token=config["BIGQUERY"]["KEY"],
        location=config["BIGQUERY"]["LOCATION"],
        tenant=get_tenant_name(config),
        shop_name=config["SHOPIFY"]["SHOP_NAME"],
        shop_token=config["SHOPIFY"]["ACCESS_TOKEN"],
        shop_api_version=config["SHOPIFY"]["API_VERSION"],
        client=None
    )
    if not extractor.has_dataset():
        extractor.create_dataset()

    for endpoint, opts in config["SHOPIFY"]["ENDPOINTS"].items():
        if not opts["ENABLED"]:
            print(f"the {endpoint} endpoint is disabled for ingestion. Skipping..")
            continue
        tables = [TableInfo(t["TYPENAME"], t["NAME"], t["SCHEMA"]) for n, t in opts["TABLES"].items()]
        extractor.migrate(tables)
        match endpoint:
            case "ORDERS":
                url = extractor.get_data(GET_ALL_ORDERS_QUERY)
                transformer = OrderTransformer(tables, 5000)
            case "CUSTOMERS":
                url = extractor.get_data(GET_ALL_CUSTOMERS_QUERY)
                transformer = CustomerTransformer(tables, 5000)
            case "PRODUCTS":
                url = extractor.get_data(GET_ALL_PRODUCTS_QUERY)
                transformer = ProductTransformer(tables, 5000)
            case _:
                print(f"No ETL available for the following endpoint:: {endpoint}. Skipping..")
                continue

        with urlopen(url) as raw_data:
            for batch in transformer.process_batched_data(raw_data):
                for table_name, data in batch.items():
                    ref = extractor.get_table_ref(table_name)
                    extractor.save_data(data, ref)
        print(f"Data successfully ingested for {endpoint}")


class ShopifyScheduledIngestionDataModel(ShopifyDataModel):
    def __init__(self, project_id, bq_token, location, tenant, shop_name, shop_token, shop_api_version, client=None):
        super().__init__(project_id, bq_token, location, tenant, shop_name, shop_token, shop_api_version, client)

    def migrate(self, tables: List[TableInfo]):
        for table in tables:
            self.create_table(table.name, get_file_from_project_root(table.schema))

    def get_data(self, query):
        return self._get_bulk_operation_run_query_url(query)

    def save_data(self, data, table):
        self.insert_json_rows(table, data)


class ShopifyScheduledIngestionTransformer(ShopifyTransformer):
    def __init__(self, table_infos: List[TableInfo], batch_size: int = 5000):
        super().__init__()
        self.batch_size = batch_size
        self.table_infos = {table_info.name: table_info for table_info in table_infos}

        # Create a mapping from typename to their corresponding table
        self.typename_to_batch = {}
        for table_name, table_info in self.table_infos.items():
            for key in table_info.key:
                self.typename_to_batch[key] = table_name

        self.batches = {name: [] for name in self.table_infos.keys()}

    @abstractmethod
    def transform_data(self, table_name, row):
        pass

    def process_batched_data(self, lines):
        for line in lines:
            decoded_line = line.decode('utf-8', 'replace')
            row = json.loads(decoded_line)

            # Determine the appropriate table and transformations based on the '__typename'
            typename = row["__typename"]
            corresponding_table = self.typename_to_batch.get(typename)

            if not corresponding_table:
                print(f"no routine found to handle the following type: {typename}")
                print(row)
                continue
            else:
                self.transform_data(corresponding_table, row)

            del row["__typename"]
            self.batches[corresponding_table].append(row)

            # Yield batches once the batch size is reached
            if len(self.batches[corresponding_table]) >= self.batch_size:
                yield {corresponding_table: self.batches[corresponding_table]}
                self.batches[corresponding_table] = []

        # Yield any remaining items
        for corresponding_table, batch in self.batches.items():
            if batch:
                yield {corresponding_table: batch}


class CustomerTransformer(ShopifyScheduledIngestionTransformer):
    def __init__(self, table_infos, batch_size):
        super().__init__(table_infos, batch_size)

    def transform_data(self, table_name, row):
        return row


class ProductTransformer(ShopifyScheduledIngestionTransformer):
    def __init__(self, table_infos, batch_size):
        super().__init__(table_infos, batch_size)

    def transform_data(self, table_name, row):
        return row


class OrderTransformer(ShopifyScheduledIngestionTransformer):
    def __init__(self, table_infos, batch_size):
        super().__init__(table_infos, batch_size)

    def transform_data(self, table_name, row):
        match table_name:
            case "shopify_orders":
                self.unpack_nested_id(row, "app")
                self.unpack_nested_id(row, "customer")
                self.unpack_money_v2(row, "subtotalPriceSet")
                self.unpack_money_v2(row, "totalPriceSet")
                self.unpack_money_v2(row, "totalDiscountsSet")
                self.unpack_money_v2(row, "totalRefundedSet")
                #Handling taxLines
                for line in row["taxLines"]:
                    self.unpack_money_v2(line, "priceSet")
                #Handling shippingLine
                if "shippingLine" in row and isinstance(row["shippingLine"], dict):
                    self.unpack_money_v2(row["shippingLine"], "discountedPriceSet")
                    self.unpack_money_v2(row["shippingLine"], "originalPriceSet")

                    if "taxLines" in row["shippingLine"] and isinstance(row["shippingLine"]["taxLines"], list):
                        for tax_line in row["shippingLine"]["taxLines"]:
                            self.unpack_money_v2(tax_line, "priceSet")


            case "shopify_customer_visits":
                pass
            case "shopify_discount_application":
                pass
            case _:
                print(f"no routine found in get_orders() to handle the following type:: {row['__typename']}")
                # print(row)
        return row


if __name__ == "__main__":
    main()
