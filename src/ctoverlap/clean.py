# Trial data cleaner
# This script extracts required fields from the raw JSON files and saves them into one cleaned CSV file

import json
import csv
from pathlib import Path
from ctoverlap.intervals import trial_interval
from ctoverlap.phases import phase_cleaner

SUPPORTED_CONDITIONS = ["colorectal cancer", "melanoma", "breast cancer"]

def clean(condition):
    condition_name = condition.lower().strip().replace(" ", "_")

    # Load the raw trial records and the matching metadata for this condition
    # Metadata is needed because extraction date and original query are part of each cleaned row

    with open(f"data/raw/{condition_name}_raw.json") as file:
        data = json.load(file)
    with open(f"data/raw/{condition_name}_metadata.json") as file:
        metadata = json.load(file)
    studies = data.get("studies", [])
    rows = []
    for study in studies:
        row = {}

        # ClinicalTrials.gov has the trial information inside nested modules
        # so each module is pulled out before selecting the needed fields
        protocol = study.get("protocolSection", {})

        identification_Module = protocol.get("identificationModule", {})
        conditions_Module = protocol.get("conditionsModule", {})
        status_Module = protocol.get("statusModule", {})
        design_Module = protocol.get("designModule", {})
        contactsLocations_Module = protocol.get("contactsLocationsModule", {})
        sponsorCollaborators_Module = protocol.get("sponsorCollaboratorsModule", {})
        armsInterventions_Module = protocol.get("armsInterventionsModule", {})

        raw_countries = []
        raw_intervention_names = []
        raw_intervention_types = []
        
        startDateStruct = status_Module.get("startDateStruct", {})
        completionDateStruct = status_Module.get("completionDateStruct", {})
        primaryCompletionDateStruct = status_Module.get("primaryCompletionDateStruct", {})
        locations = contactsLocations_Module.get("locations", [])

        # A single trial can have multiple listed locations so countries are collected first
        # and then stored together in one CSV cell.

        for loc in locations:
            country = loc.get("country")
            raw_countries.append(country)
        lead_Sponsor = sponsorCollaborators_Module.get("leadSponsor", {})
        interventions = armsInterventions_Module.get("interventions", [])
        for inter in interventions:
            inter_name = inter.get("name")
            raw_intervention_names.append(inter_name)
            inter_type = inter.get("type")
            raw_intervention_types.append(inter_type)

        nct_id = identification_Module.get("nctId", "")
        brief_title = identification_Module.get("briefTitle", "")
        condition_names = conditions_Module.get("conditions", "")
        overall_status = status_Module.get("overallStatus", "")
        start_date = startDateStruct.get("date", "")
        completion_date = completionDateStruct.get("date", "")
        primary_completion = primaryCompletionDateStruct.get("date", "")
        phase = design_Module.get("phases", "")
        sponsor_name = lead_Sponsor.get("name", "")
        extraction_date = metadata.get("extraction_date", "")
        original_condition_query = metadata.get("condition_query", "")

        # Remove missing values before combining repeated fields into comma separated strings
        final_countries = list(filter(None, raw_countries))
        final_intervention_names = list(filter(None, raw_intervention_names))
        final_intervention_types = list(filter(None, raw_intervention_types))

        cleaned_phase = phase_cleaner(phase)

        row["NCT ID"] = nct_id
        row["brief title"] = brief_title
        row["condition names"] = condition_names
        row["overall trial status"] = overall_status
        row["start date"] = start_date
        row["completion date"] = completion_date
        row["primary completion date"] = primary_completion
        row["phase"] = cleaned_phase
        row["countries"] = final_countries
        row["sponsor name"] = sponsor_name
        row["intervention types"] = final_intervention_types
        row["intervention names"] = final_intervention_names
        row["extraction date"] = extraction_date
        row["original condition query"] = original_condition_query
        final_start, final_end, end_source, overlap_eligible, exclusion_reason = trial_interval(row)

        row["start_date"] = final_start
        row["end_date"] = final_end
        row["end_date_source"] = end_source
        row["overlap_eligible"] = overlap_eligible
        row["exclusion_reason"] = exclusion_reason

        rows.append(row)

    return rows

def clean_all():
    all_rows = []
    excluded_rows = []

    # Clean each supported condition and combine the rows
    for conditions in SUPPORTED_CONDITIONS:
        condition_rows = clean(conditions)

        for item in condition_rows:
            if item.get("overlap_eligible") is False:
                excluded_rows.append(item)
        all_rows.extend(condition_rows)
        
    return all_rows, excluded_rows

def save_cleaned():
    output_path = Path("data/processed/cleaned_trials.csv")
    excluded_output_path = Path("data/processed/excluded_trials.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    cleaned_data, excluded_data = clean_all()

    if not cleaned_data:
        print("No data found")
        return
    with open(output_path, newline="", mode="w", encoding="utf-8") as file:

        headers = cleaned_data[0].keys()

        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(cleaned_data)
        print(f"""
              Saved cleaned data to data/processed/cleaned_trials.csv
              Number of rows saved: {len(cleaned_data)}
              """)

    with open(excluded_output_path, newline="", mode="w", encoding="utf-8") as file:

        headers = excluded_data[0].keys()
        
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()

        if excluded_data:
            writer.writerows(excluded_data)

        print(f"""
            Saved excluded data to data/processed/excluded_trials.csv
            Number of rows saved: {len(excluded_data)}
            """)
