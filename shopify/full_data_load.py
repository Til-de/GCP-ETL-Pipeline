from typing import Type

from DMOT import Extractor
from constants import PROJECT_ID
from query import GET_ALL_ORDERS_QUERY
import yaml


class TableReference:
    def __init__(self, name, schema):
        self.name = name
        self.schema = schema


def orders(extractor):

    extractor.migrate()
def main():
    with open('config.yaml', 'rt') as f:
        config = yaml.safe_load(f.read())

    extractor = FullDataExtractor()








class FullDataExtractor(Extractor):
    def __init__(self, project_id, shop_name, token):
        super().__init__(project_id, shop_name, token)

    def migrate(self, tables: Type[TableReference]):
        self.create_dataset()
        for table in tables:
            self.create_table(self.client. self.dataset, table.name, table.schema)

    def get_data(self, query):
        self._get_bulk_operation_run_query_url(query)

    def save_data(self, table, data):
        self.insert_json_rows(table, data)


if __name__ == "__main__":
    main()

