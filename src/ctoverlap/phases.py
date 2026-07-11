# Phase cleaner
# This script converts ClinicalTrials.gov phase values into consistent phase buckets

POSSIBLE_PHASES = {
    ("EARLY_PHASE1",): "Early Phase 1",
    ("PHASE1",): "Phase 1",
    ("PHASE2",): "Phase 2",
    ("PHASE3",): "Phase 3",
    ("PHASE4",): "Phase 4",
    ("PHASE1", "PHASE2"): "Phase 1/2",
    ("PHASE2", "PHASE3"): "Phase 2/3",
}



def phase_cleaner(phase):
    if phase is None or phase == "" or phase == []:
        return "Unspecified / Not Applicable"

    # Support for plain strings
    if isinstance(phase, str):
        phase = [phase]

    if not isinstance(phase, list):
        return "Unspecified / Not Applicable"
    
    cleaned_list = set()

    for item in phase:
        if isinstance(item, str) and item.strip():
            clean_item = item.strip().upper()
            cleaned_list.add(clean_item)

    if not cleaned_list or cleaned_list == {"NA"}:
        return "Unspecified / Not Applicable"

    # Convert to a sorted tuple to match the dictionary keys in POSSIBLE_PHASES
    return POSSIBLE_PHASES.get(tuple(sorted(cleaned_list)), "Unspecified / Not Applicable")