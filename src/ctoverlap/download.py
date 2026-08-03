# Raw data downloader
# This script downloads ClinicalTrials.gov records for the supported cancer conditions and saves the raw JSON plus extraction metadata

import requests
import json
from datetime import datetime, timezone
from pathlib import Path

API_URL = "https://clinicaltrials.gov/api/v2/studies"
DEFAULT_CONDITION = "colorectal cancer"
PROJECT_VERSION = "0.1.0"
SUPPORTED_CONDITIONS = ["colorectal cancer", "melanoma", "breast cancer"]

def fetch_studies(condition):
    all_studies = []
    next_page_token = None

    while True:
        parameters = {
            "query.cond" : condition,
            "format" : "json",
            "pageSize": 1000,
            "countTotal": "true"
        }

        if next_page_token is not None:
            parameters["pageToken"] = next_page_token

        response = requests.get(API_URL, params=parameters, timeout=60)
        response.raise_for_status()
        data = response.json()

        studies = data.get("studies", [])
        all_studies.extend(studies)

        print(f"Downloaded {len(all_studies)} records")
        print(f"for {condition}")

        next_page_token = data.get("nextPageToken")

        if not next_page_token:
            break

        return {"studies": all_studies,
                "totalCount": len(all_studies),
                }


def save_json(data, output_path):
    with open (output_path, "w") as json_file:
        json.dump(data, json_file)

def download_one_condition(condition=DEFAULT_CONDITION):
    parent_dir = Path("data")
    raw_path = parent_dir / "raw"
    raw_path.mkdir(parents=True, exist_ok=True)

    condition_name = condition.lower().strip().replace(" ", "_")

    data = fetch_studies(condition)

    # Saved because ongoing trials without end dates are counted only up to this date
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

    print(f"Download for {condition} has been successfully completed!")
    print(f"Number of records downloaded: {len(studies)}")
    print(f"The records have been saved to {raw_output_path}")
    print(f"The metadata has been saved to {metadata_output_path}")
    
def download_all():
    # The first version of this project intentionally supports only these three conditions
    for condition in SUPPORTED_CONDITIONS:
        download_one_condition(condition)