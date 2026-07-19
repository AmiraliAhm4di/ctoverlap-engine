# Clinical trial date parser
# This script converts ClinicalTrials.gov date strings into Python date objects for later analysis

from datetime import datetime

# Common text values that mean there is no data
NO_DATA_VALUES = [
    "unknown", 
    "n/a", 
    "not available", 
    "na", 
    "none", 
    "null", 
    "missing", 
    "not provided", 
    "not listed"
    ]

# Common date formats used
DATE_FORMATS = [
    "%B %d, %Y", 
    "%B %Y", 
    "%Y", 
    "%m/%d/%Y", 
    "%Y-%m", 
    "%Y-%m-%d"
    ]


def parse_trial_date(date_string):

    if date_string is None:
        return None
    
    date_string = date_string.strip().lower()

    if date_string == "":
        return None

    if date_string in NO_DATA_VALUES:      
        return None

    # Try each date format until one parses
    for formats in DATE_FORMATS:
        try:
            return datetime.strptime(date_string, formats).date()
        except ValueError:
            pass

    return None