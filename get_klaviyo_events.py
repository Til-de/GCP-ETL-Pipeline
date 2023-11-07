import requests
from google.cloud import bigquery
from dotenv import load_dotenv
import os
import json

load_dotenv()

project_id = str("diacritic")
client = bigquery.Client(project = project_id)
dataset = client.dataset('klaviyo_reports')
table = dataset.table('klaviyo_events')
api_key = os.getenv('KLAVIYO_API_KEY')


url = "https://a.klaviyo.com/api/events/?page[cursor]&fields[event]=timestamp,profile_id,metric_id"
payload = {}
headers = {
 'revision': '2023-02-22',
  'Accept': 'application/json',
    'Content-Type': 'application/json',
  'Authorization': f'Klaviyo-API-Key {api_key}'
}
page_count = 0

def convert_nested_dict_to_json_string(data: dict):
    for key, value in data.items():
        if isinstance(value, dict) or isinstance(value, list):
            data[key] = json.dumps(value)
    return data
def add_data_to_bq(data):
    job_config = bigquery.LoadJobConfig()
    job_config.source_format = bigquery.SourceFormat.NEWLINE_DELIMITED_JSON
    job = client.load_table_from_json(data, table, job_config=job_config)
    print(job.result())

while url:

    # Send a GET request to the current URL
    response = requests.request("GET", url, headers = headers, data = payload)
    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        page_count += 1

        print(f"Retrieved page {page_count}")

        # Check if there's a "next" cursor link
        if 'next' in data['links']:
            url = data['links']['next']
        else:
            # No more "next" cursor link, exit the loop
            url = None

        add_data_to_bq(data['data'])

    else:
        # Handle any errors that occur during the request
        print(f"Error: {response.status_code}")
        break


print("Finished retrieving all pages and inserting data into BQ")

#response = requests.request("GET", url, headers = headers, data = payload)
#data_dict = response.json()
#print(json.dumps(data_dict, indent=4, sort_keys=True))

#Retrieved up to page 309