# Clinical trial date parser
# This script converts ClinicalTrials.gov date strings into python date objects for later analysis

from datetime import datetime

# Common text values that mean there is no data
nodata_values = ["unknown", "n/a", "not available", "na", "none", "null", "missing", "not provided", "not listed"]

# Common date formats used
formats = ["%B %d, %Y", "%B %Y", "%Y", "%m/%d/%Y", "%Y-%m", "%Y-%m-%d"]

def parse_trial_date(date):

    if date == None:
        return None
    
    date = date.strip().lower()

    if date == "":
        return None

    if date in nodata_values:
        return None

    # Try each date format until one parses
    for x in formats:
        try:
            return datetime.strptime(date, x).date()
        except ValueError:
            pass

    return None