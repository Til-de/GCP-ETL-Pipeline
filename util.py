import os

import yaml


def kebab_case_to_snake_case(word):
    return "_".join(word.lower().split('-'))


def get_config():
    with open(get_file_from_project_root('config.yaml'), 'rt') as f:
        config = yaml.safe_load(f.read())
    return config


def get_root_dir():
    return os.path.dirname(os.path.abspath(__file__))


def get_file_from_project_root(filename: str):
    return os.path.join(get_root_dir(), filename)


def get_tenant_name(config):
    tenant = config["BIGQUERY"]["TENANT_NAME"]
    if not tenant:
        tenant = config["BIGQUERY"]["SHOP_NAME"]
    return tenant
