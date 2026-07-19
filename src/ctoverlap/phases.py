# Phase cleaner
# This script converts ClinicalTrials.gov phase values into consistent phase buckets

POSSIBLE_PHASES = {
    frozenset({"EARLY_PHASE1"}): "Early Phase 1",
    frozenset({"PHASE1"}): "Phase 1",
    frozenset({"PHASE2"}): "Phase 2",
    frozenset({"PHASE3"}): "Phase 3",
    frozenset({"PHASE4"}): "Phase 4",
    frozenset({"PHASE1", "PHASE2"}): "Phase 1/2",
    frozenset({"PHASE2", "PHASE3"}): "Phase 2/3",
}

MISSING_PHASE_VALUES = {
    "",
    "NOT_APPLICABLE",
    "NONE",
    "N/A",
    "NA",
    "UNSPECIFIED",
    "UNKNOWN",
    "NULL",
    "NOT APPLICABLE",
}

VALID_PHASE_VALUES = set().union(*POSSIBLE_PHASES)

def phase_cleaner(phase_value):
    if phase_value is None:
        return "Unspecified / Not Applicable"
    
    # Support for plain strings
    if isinstance(phase_value, str):
        phase_value = [phase_value]

    # Reject unexpected input types
    if not isinstance(phase_value, (list, tuple)):
        return "Unspecified / Not Applicable"
    
    # Set stops duplicate phase values
    cleaned_phases = set()

    for phase_item in phase_value:
        if not isinstance(phase_item, str):
            continue

        cleaned_phase = phase_item.strip().upper()
        if cleaned_phase in MISSING_PHASE_VALUES:
            continue

        if cleaned_phase not in VALID_PHASE_VALUES:
            return "Unspecified / Not Applicable"

        cleaned_phases.add(cleaned_phase)
    if not cleaned_phases:
        return "Unspecified / Not Applicable"
    
    # Match the cleaned phase values to the correct phase category
    return POSSIBLE_PHASES.get(frozenset(cleaned_phases),"Unspecified / Not Applicable",)