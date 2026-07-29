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

def get_intervals_by_phase(condition, phase):
    con = duckdb.connect(str(DUCKDB_DATABASE))
    query = """
    SELECT start_date, end_date
    FROM trials
    WHERE overlap_eligible = TRUE
    AND "phase" = ?
    AND "original condition query" = ?;
    """
    result = con.execute(query, [phase, condition]).fetchall()
    con.close()
    return result



def get_phases_for_condition(condition):
    con = duckdb.connect(str(DUCKDB_DATABASE))
    query = """
    SELECT DISTINCT "phase"
    FROM trials
    WHERE overlap_eligible = TRUE
    AND "original condition query" = ?
    ORDER BY "phase";
    """
    result = con.execute(query, [condition]).fetchall()

    phases = []
    for phase in result:
        phases.append(phase[0])

    con.close()
    return phases


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

def build_phase_density_rows(condition, phase):
    raw_intervals = get_intervals_by_phase(condition, phase)
    converted_intervals = convert_intervals(raw_intervals)
    trial_total = len(converted_intervals)

    if trial_total < 5:
        skipped_row = (
            None,
            "condition_phase",
            condition,
            phase,
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
            "condition_phase",
            condition,
            phase,
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


def get_countries_for_condition(condition):
    con = duckdb.connect(str(DUCKDB_DATABASE))
    query = """
    SELECT DISTINCT trial_countries.country_name
    FROM trials
    JOIN trial_countries
    ON trials."NCT ID" = trial_countries.nct_id
    WHERE trials.overlap_eligible = TRUE
    AND trials."original condition query" = ?
    ORDER BY trial_countries.country_name;
    """
    result = con.execute(query, [condition]).fetchall()

    countries = []
    for country in result:
        countries.append(country[0])

    con.close()
    return countries

def get_intervals_by_country(condition, country):
    con = duckdb.connect(str(DUCKDB_DATABASE))
    query = """
    SELECT trials.start_date, trials.end_date
    FROM trials
    JOIN trial_countries
    ON trials."NCT ID" = trial_countries.nct_id
    WHERE trials.overlap_eligible = TRUE
    AND trial_countries.country_name = ?
    AND trials."original condition query" = ?;
    """
    result = con.execute(query, [country, condition]).fetchall()
    con.close()
    return result


def build_country_density_rows(condition, country):
    raw_intervals = get_intervals_by_country(condition, country)
    converted_intervals = convert_intervals(raw_intervals)
    trial_total = len(converted_intervals)

    if trial_total < 5:
        skipped_row = (
            None,
            "condition_country",
            condition,
            None,
            country,
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
            "condition_country",
            condition,
            None,
            country,
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


def get_intervention_types_for_condition(condition):
    con = duckdb.connect(str(DUCKDB_DATABASE))
    query = """
    SELECT DISTINCT trial_interventions.intervention_type
    FROM trials
    JOIN trial_interventions
    ON trials."NCT ID" = trial_interventions.nct_id
    WHERE trials.overlap_eligible = TRUE
    AND trials."original condition query" = ?
    AND trial_interventions.intervention_type IS NOT NULL
    ORDER BY trial_interventions.intervention_type;
    """
    result = con.execute(query, [condition]).fetchall()

    intervention_types = []
    for intervention_type in result:
        intervention_types.append(intervention_type[0])

    con.close()
    return intervention_types

def get_intervals_by_intervention_type(condition, intervention_type):
    con = duckdb.connect(str(DUCKDB_DATABASE))
    query = """
    SELECT trials.start_date, trials.end_date
    FROM trials
    JOIN (
        SELECT DISTINCT nct_id, intervention_type
        FROM trial_interventions
    ) AS intervention_groups
    ON trials."NCT ID" = intervention_groups.nct_id
    WHERE trials.overlap_eligible = TRUE
    AND intervention_groups.intervention_type = ?
    AND trials."original condition query" = ?;
    """
    result = con.execute(query, [intervention_type, condition]).fetchall()
    con.close()
    return result


def build_intervention_density_rows(condition, intervention_type):
    raw_intervals = get_intervals_by_intervention_type(condition, intervention_type)
    converted_intervals = convert_intervals(raw_intervals)
    trial_total = len(converted_intervals)

    if trial_total < 5:
        skipped_row = (
            None,
            "condition_intervention_type",
            condition,
            None,
            None,
            intervention_type,
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
            "condition_intervention_type",
            condition,
            None,
            None,
            intervention_type,
            active_count,
            started_this_month,
            ended_this_month,
            trial_total,
            True,
            None,
        )
        finished_rows.append(density_row)

    return finished_rows

def build_all_density_rows():
    conditions = [
        "colorectal cancer",
        "melanoma",
        "breast cancer",
    ]

    finished_rows = []

    for condition in conditions:
        condition_rows = build_condition_density_rows(condition)
        finished_rows.extend(condition_rows)

        phases = get_phases_for_condition(condition)

        for phase in phases:
            phase_rows = build_phase_density_rows(condition, phase)
            finished_rows.extend(phase_rows)

        countries = get_countries_for_condition(condition)

        for country in countries:
            country_rows = build_country_density_rows(condition, country)
            finished_rows.extend(country_rows)

        intervention_types = get_intervention_types_for_condition(condition)

        for intervention_type in intervention_types:
            intervention_rows = build_intervention_density_rows(
                condition,
                intervention_type,
            )
            finished_rows.extend(intervention_rows)

    return finished_rows


def load_monthly_density():
    finished_rows = build_all_density_rows()

    con = duckdb.connect(str(DUCKDB_DATABASE))

    con.execute("""DELETE FROM monthly_density;""")

    query = """
    INSERT INTO monthly_density (
        month,
        stratum_type,
        condition_query,
        phase_bucket,
        country,
        intervention_type,
        active_trial_count,
        started_trials,
        ended_trials,
        trial_count_total,
        group_analyzed,
        skip_reason
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """

    if len(finished_rows) > 0:
        con.executemany(query, finished_rows)

    database_count = con.execute(
        """SELECT COUNT(*) FROM monthly_density"""
    ).fetchone()[0]

    print(f"Python rows prepared: {len(finished_rows)}")
    print(f"Database rows inserted: {database_count}")

    con.close()

if __name__ == "__main__":
    load_monthly_density()