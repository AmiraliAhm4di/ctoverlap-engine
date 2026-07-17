# Brute-force overlap baseline
# This script checks every trial interval for each month and counts how many trials were active to compare with sweep line

from ctoverlap.sweep_line import next_month


def brute_force(intervals):
    monthly_counts = {}
    if not intervals:
        return monthly_counts

    # Bounderies needed for the full timeline
    start_months = []
    end_months = []

    for start, end in intervals:
        start_months.append(start)
        end_months.append(end)

    earliest = min(start_months)
    latest = max(end_months)

    # Build every month from the earliest start to the latest end
    months = []
    current_month = earliest

    while current_month <= latest:
        months.append(current_month)
        current_month = next_month(current_month)

    # Check every trial during every month and count the active ones
    for month in months:
        active_count = 0

        for start, end in intervals:
            # The start and end months are both included as active
            if start <= month <= end:
                active_count += 1
        monthly_counts[month] = active_count

    return monthly_counts