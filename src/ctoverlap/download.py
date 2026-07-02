import requests
import json
from datetime import datetime, timezone
from pathlib import Path
import os


API_URL = "https://clinicaltrials.gov/api/v2/studies"
DEFAULT_CONDITION = "colorectal cancer"
PROJECT_VERSION = "0.1.0"

def fetch_studies(condition):
    parameters = {
        "query.cond" : condition,
        "format" : "json",
        "pageSize": 1000,
        "countTotal": "true"
    }
    response = requests.get(API_URL, params=parameters, timeout=20)
    response.raise_for_status()
    data = response.json()
    return data

def save_json(data, output_path):
    with open (output_path, "w") as json_file:
        json.dump(data, json_file)

def download_one_condition(condition="colorectal cancer"):
    parent_dir = Path("data")
    raw_path = parent_dir / "raw"
    raw_path.mkdir(parents=True, exist_ok=True)

    condition_name = condition.lower().strip().replace(" ", "_")

    data = fetch_studies(condition)

    extraction_date = datetime.now(timezone.utc).isoformat()

    studies = data.get("studies", [])

    metadata = {
        "condition_query": condition,
        "extraction_date": extraction_date,
        "number_of_records_downloaded": len(studies),
        "source_name": API_URL,
        "project_version": PROJECT_VERSION,
    }

    raw_output_path = raw_path / f"{condition_name}_raw.json"
    metadata_output_path = raw_path / f"{condition_name}_metadata.json"


    save_json(data, raw_output_path)
    save_json(metadata, metadata_output_path)

    print(f"""
        Download for {condition} has been successfully completed!
        Number of records downloaded: {len(studies)}
        The records have been saved to {raw_output_path}
        The metadata has been saved to {metadata_output_path}
          """)