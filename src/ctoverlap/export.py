# Export analysis tables
# This script reads analysis results from DuckDB and saves them as CSV files for the R report

from pathlib import Path
import duckdb

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
DATABASE = PROJECT_ROOT / "data" / "database"
DUCKDB_DATABASE = DATABASE / "clinical_trials.duckdb"
OUTPUT_PATH = PROJECT_ROOT / "outputs" / "tables"

def export_condition_density():
    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(DUCKDB_DATABASE))
    output_file = OUTPUT_PATH / "monthly_density_by_condition.csv"

    query1 = f"""
    COPY (
        SELECT
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
        FROM monthly_density
        WHERE stratum_type = 'condition'
        ORDER BY condition_query, month
    )
    TO '{output_file.as_posix()}'
    (
        FORMAT CSV,
        HEADER
    );
    """

    con.execute(query1)
    con.close()
    print("Condition density export complete")

def export_condition_phase_density():
    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(DUCKDB_DATABASE))
    output_file = OUTPUT_PATH / "monthly_density_by_condition_phase.csv"

    query1 = f"""
    COPY (
        SELECT
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
        FROM monthly_density
        WHERE stratum_type = 'condition_phase'
        ORDER BY condition_query, phase_bucket, month
    )
    TO '{output_file.as_posix()}'
    (
        FORMAT CSV,
        HEADER
    );
    """

    con.execute(query1)
    con.close()
    print("Condition phase density export complete")

def export_condition_country_density():
    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(DUCKDB_DATABASE))
    output_file = OUTPUT_PATH / "monthly_density_by_condition_country.csv"

    query1 = f"""
    COPY (
        SELECT
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
        FROM monthly_density
        WHERE stratum_type = 'condition_country'
        ORDER BY condition_query, country, month
    )
    TO '{output_file.as_posix()}'
    (
        FORMAT CSV,
        HEADER
    );
    """

    con.execute(query1)
    con.close()
    print("Condition country density export complete")

def export_condition_intervention_density():
    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(DUCKDB_DATABASE))
    output_file = OUTPUT_PATH / "monthly_density_by_condition_intervention_type.csv"

    query1 = f"""
    COPY (
        SELECT
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
        FROM monthly_density
        WHERE stratum_type = 'condition_intervention_type'
        ORDER BY condition_query, intervention_type, month
    )
    TO '{output_file.as_posix()}'
    (
        FORMAT CSV,
        HEADER
    );
    """

    con.execute(query1)
    con.close()
    print("Condition intervention density export complete")

def export_all_density():
    export_condition_density()
    export_condition_phase_density()
    export_condition_country_density()
    export_condition_intervention_density()