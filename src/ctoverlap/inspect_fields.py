# Field inspection script
# This script loads one raw ClinicalTrials.gov JSON file and prints key fields from the first 3 studies

import json

def inspect_fields(condition):
    condition_name = condition.lower().strip().replace(" ", "_")

    with open(f"data/raw/{condition_name}_raw.json") as file:
        data = json.load(file)
    studies = data.get("studies", [])
    print(f"""
    Inspecting {condition}
    Number of studies downloaded: {len(studies)}
    Showing the first 3 studies:
          """)
    n = 3
    multistudies = studies[:n]

    # ClinicalTrials.gov stores most useful fields inside protocolSection modules
    # This dictionary records the module and field name needed to locate each value
    fields = {
        "NCT ID": ("identificationModule", "nctId"),
        "Brief title": ("identificationModule", "briefTitle"),
        "Official title": ("identificationModule", "officialTitle"),
        "Overall status": ("statusModule", "overallStatus"),
        "Start date": ("statusModule", "startDateStruct"),
        "Primary completion date": ("statusModule", "primaryCompletionDateStruct"),
        "Completion date": ("statusModule", "completionDateStruct"),
        "Sponsor name": ("sponsorCollaboratorsModule", "leadSponsor"),
        "Condition names": ("conditionsModule", "conditions"),
        "Phase": ("designModule", "phases"),
        "Study type": ("designModule", "studyType"),
        "Enrollment": ("designModule", "enrollmentInfo"),
        "Country": ("contactsLocationsModule", "locations"),
        "Intervention type/name": ("armsInterventionsModule", "interventions"),
    }
    trial_count = 1
    for study in multistudies:
        print("\n--------------------------------------------")
        print(f"Trial {trial_count}")
        protocol = study.get("protocolSection", {})
        
        for label, (module, field) in fields.items():
            value = protocol.get(module, {}).get(field)
            print(f"{label}: {value if value is not None else 'missing'}")
        trial_count += 1