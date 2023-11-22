import time
from abc import abstractmethod
from urllib import error
from urllib.request import urlopen

import requests

from DMOT import DataModel, Transformer
from errors import GraphQLQueryError, BulkOperationError
from query import BULK_OPERATION_RUN_QUERY, BULK_OPERATION_STATUS

POLL_INTERVAL_SECONDS = 30


class ShopifyDataModel(DataModel):
    def __init__(self, project_id, bq_token, location, tenant, shop_name, shop_token, shop_api_version, client=None):
        super().__init__(project_id, bq_token, location, tenant, client)
        self._headers = {'X-Shopify-Access-Token': shop_token, 'Content-Type': 'application/json'}
        self.url = f"https://{shop_name}.myshopify.com/admin/api/{shop_api_version}/graphql.json"

    @abstractmethod
    async def get_data(self, query):
        pass

    def _get_bulk_operation_run_query_url(self, query):
        response = requests.post(url=self.url, headers=self._headers, json={
            "query": BULK_OPERATION_RUN_QUERY,
            "variables": {
                "subquery": query
            }
        })
        print(f"response {response.status_code} for BulkOperationRunQuery")
        if response.status_code == 200:
            while True:
                op_state = requests.post(url=self.url, headers=self._headers, json={
                    "query": BULK_OPERATION_STATUS,
                })
                json_data = op_state.json()
                status = json_data['data']['currentBulkOperation']['status']
                error_code = json_data['data']['currentBulkOperation']['errorCode']
                if error_code is not None:
                    raise BulkOperationError(error_code, f"Error returned by BulkOperationRunQuery:{error_code}")
                if status == "COMPLETED":

                    try:
                        url = json_data['data']['currentBulkOperation']['url']
                        print(f"Bulk operation complete -> {url} ")
                        return url
                    except error.HTTPError as e:
                        print(f"HTTP Error: {e.code}. {e.reason}")
                time.sleep(POLL_INTERVAL_SECONDS)
        else:
            raise GraphQLQueryError(response.status_code,
                                    f"GraphQL query failed with status code {response.status_code}")


class ShopifyTransformer(Transformer):
    def __init__(self):
        super().__init__()

    def unpack_nested_id(self, row, prop):
        if row[prop]:
            id = row[prop]["id"]
            row[prop] = id

    def unpack_money_v2(self, root: dict, prop: str):
        try:
            if root[prop]:
                if root[prop]["shopMoney"]:
                    root[prop] = root[prop]["shopMoney"]["amount"]
                elif root[prop]["presentmentMoney"]:
                    root[prop] = root[prop]["presentmentMoney"]["amount"]
        except KeyError as e:
            print(f"KeyError: {e}")
        except Exception as e:
            print(f"Error: {e}")


    @abstractmethod
    def process_batched_data(self, data):
        pass
