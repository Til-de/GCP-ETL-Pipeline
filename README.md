
# GCP ETL Pipeline Scripts

Scripts for scheduled data ingestion into GCP from the following data sources:
    
- Shopify



## Authors

- [@therealchrisrock](https://www.github.com/therealchrisrock)



## Installation

Rename `sample.config.yaml` to `config.yaml` and fill in the missing fields. Ensure that your Shopify app has the following access scopes:

- read_customers
- read_orders
- read_products

And that your GCP service account is assigned `roles/bigquery.dataEditor`

Install dependencies with pip:

```bash
  pip install -r requirements.txt
```
## Usage/Examples
To run a full data ingestion:

```bash
python shopify/full_data_load.py
```
