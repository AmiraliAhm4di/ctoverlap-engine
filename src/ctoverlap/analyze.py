# Analysis module
# This script retrieves trial intervals from DuckDB and separates them into analysis groups
# then calculates monthly overlap and prepares rows for the monthly_density table

from pathlib import Path
import duckdb
from ctoverlap.sweep_line import sweep_line
from ctoverlap.sweep_line import dates_into_months
from ctoverlap.sweep_line import next_month
from ctoverlap.sweep_line import previous_month
from datetime import date


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
DATABASE = PROJECT_ROOT / "data" / "database"
DUCKDB_DATABASE = DATABASE / "clinical_trials.duckdb"


def get_interval_one_condition(condition):
    con = duckdb.connect(str(DUCKDB_DATABASE))
    query = """
    SELECT start_date, end_date
    FROM trials
    WHERE overlap_eligible = TRUE
    AND "original condition query" = ?;
    """
    result = con.execute(query, [condition]).fetchall()
    con.close()
    return result



def convert_intervals(intervals):
    converted_intervals = []

    for start, end in intervals:
        start_v1 = start.strftime("%Y-%m-%d")
        new_start = dates_into_months(start_v1)

        end_v1 = end.strftime("%Y-%m-%d")
        new_end = dates_into_months(end_v1)

        converted_intervals.append((new_start, new_end))

    return converted_intervals


def start_end_counter(intervals):
    start_count = {}
    end_count = {}

    for start, end in intervals:
        if start in start_count:
            start_count[start] += 1
        else:
            start_count[start] = 1

        if end in end_count:
            end_count[end] += 1
        else:
            end_count[end] = 1

    return start_count, end_count


def build_condition_density_rows(condition):
    raw_intervals = get_interval_one_condition(condition)
    converted_intervals = convert_intervals(raw_intervals)
    trial_total = len(converted_intervals)

    if trial_total < 5:
        skipped_row = (
            None,
            "condition",
            condition,
            None,
            None,
            None,
            None,
            None,
            None,
            trial_total,
            False,
            "fewer_than_5_trials",
        )
        return [skipped_row]

    start_count, end_count = start_end_counter(converted_intervals)
    maximum_overlap, event_month_counts, complete_monthly_counts = sweep_line(converted_intervals)

    finished_rows = []
    for month, active_count in complete_monthly_counts.items():
        started_this_month = start_count.get(month, 0)
        ended_this_month = end_count.get(month, 0)

        density_row = (
            month,
            "condition",
            condition,
            None,
            None,
            None,
            active_count,
            started_this_month,
            ended_this_month,
            trial_total,
            True,
            None,
        )
        finished_rows.append(density_row)

    return finished_rows

rows = build_condition_density_rows("breast cancer")
print(len(rows))
print(rows[:5])
print(rows[-5:])
print(max(rows, key=lambda row: row[6]))

# print(sum(start_count.values()))
# print(sum(end_count.values()))
# print(len(converted_intervals))
# print(f"""
# Maximum overlap: {maximum_overlap} 
# Number of event months: {len(event_month_counts)}, 
# Number of complete timeline months: {len(complete_monthly_counts)}
# {first_five_complete}
# {last_five_complete}
# """)