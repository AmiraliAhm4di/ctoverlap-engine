# Active trial interval rules
# This script makes the cleaned trial date and status fields overlap ready

from ctoverlap.dates import parse_trial_date

# Status groups are used only when a trial has no usable completion date
NOT_ENDED_STATUSES = {
    "active_not_recruiting",
    "recruiting",
    "not_yet_recruiting",
    "enrolling_by_invitation",
}

ENDED_STATUSES = {
    "completed",
    "terminated",
    "withdrawn",
    "suspended",
}

def extraction_cleaner(timestamp):
    # Extraction timestamps have time data as well but the interval logic only needs the date
    if not isinstance(timestamp, str):
        return None

    return timestamp[:10]

def trial_interval(data):

    start_date = data["start date"]
    completion_date = data["completion date"]
    primary_completion_date = data["primary completion date"]
    overall_status = data["overall trial status"]
    extraction_date = data["extraction date"]

    start_final = parse_trial_date(start_date)
    completion_final = parse_trial_date(completion_date)
    primary_final = parse_trial_date(primary_completion_date)

    overall_final = overall_status.strip().lower()
    extraction_final = parse_trial_date(extraction_cleaner(extraction_date))

    # A trial cannot be analyzed if it doesn't have a start date
    if start_final is None:
        return None, None, "missing", False, "missing_start_date"
    
    # Use the completion date if it exists
    if completion_final is not None:
        return start_final, completion_final, "completion_date", True, None
    
    # if not, use the primary completion date if available
    elif primary_final is not None:
        return start_final, primary_final, "primary_completion_date", True, None
    
    # Ongoing trials with no end date stay active until the data was downloaded
    elif overall_final in NOT_ENDED_STATUSES:
        return start_final, extraction_final, "extraction_date_for_ongoing_trial", True, None
    
    # Closed trials without an end date cannot be used
    elif overall_final in ENDED_STATUSES:
        return start_final, None, "missing", False, "missing_end_date_for_closed_trial"
    
    # Exclude ones with an unknown status and no end date
    else:
        return start_final, None, "missing", False, "missing_end_date_unknown_status"