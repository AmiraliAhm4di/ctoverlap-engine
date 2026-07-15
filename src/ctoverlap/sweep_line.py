# Monthly trial overlap calculator
# This script records trial start and end dates and calculates how many are active during each month

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

def dates_into_months(data):
    return data[:-3]

def next_month(data):

    current_date = datetime.strptime(data, "%Y-%m")
    next_date = current_date + relativedelta(months=1)

    return next_date.strftime("%Y-%m")

def previous_month(data):

    current_date = datetime.strptime(data, "%Y-%m")
    next_date = current_date - relativedelta(months=1)

    return next_date.strftime("%Y-%m")


def sweep_line(intervals):
    events = {}
    monthly_counts = {}


    # Add a trial when it starts and remove it after its ending month
    for start, end in intervals:
        events[start] = events.get(start, 0) + 1

        final_end = next_month(end)
        events[final_end] = events.get(final_end, 0) - 1
    events = sorted(events.items())

    current_concurrent = 0
    max_concurrent = 0

    # Go through the events in order and keep track of active trials
    for month, event_type in events:
        current_concurrent = current_concurrent + event_type
        max_concurrent = max(max_concurrent, current_concurrent)
        monthly_counts[month] = current_concurrent

    complete_counts = {}
    if not events:
        return 0, {}, {}
    
    current_month = events[0][0]
    last_month = previous_month(events[-1][0])

    current_count = 0

    # Fill in months where no trial started or ended
    while current_month <= last_month:
        if current_month in monthly_counts:
            current_count = monthly_counts[current_month]

        complete_counts[current_month] = current_count
        current_month = next_month(current_month)


    return max_concurrent, monthly_counts, complete_counts


