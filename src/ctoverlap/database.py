# Database builder
# This script creates the local DuckDB database and loads the project's processed data

from pathlib import Path
import duckdb
import ast
import json

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
DATABASE = PROJECT_ROOT / "data" / "database"
CLEANED_TRIALS_CSV = DATA_PROCESSED / "cleaned_trials.csv"
EXCLUDED_TRIALS_CSV = DATA_PROCESSED / "excluded_trials.csv"
DUCKDB_DATABASE = DATABASE / "clinical_trials.duckdb"

def connect_to_database():
    DATABASE.mkdir(parents=True, exist_ok=True)
    connection = duckdb.connect(str(DUCKDB_DATABASE))
    return connection

connection = connect_to_database()

if DUCKDB_DATABASE.exists():
    print(f"Database exists: {DUCKDB_DATABASE}")
else:
    print(f"Database was not created: {DUCKDB_DATABASE}")

connection.close()

def load_trials():
    con = connect_to_database()

    cleaned_csv_string = CLEANED_TRIALS_CSV.as_posix()
    excluded_csv_string = EXCLUDED_TRIALS_CSV.as_posix()

    con.execute(f"CREATE OR REPLACE TABLE trials AS SELECT * FROM read_csv_auto('{cleaned_csv_string}')")
    print("Finished loading cleaned trials!")

    con.execute(f"CREATE OR REPLACE TABLE excluded_trials AS SELECT * FROM read_csv_auto('{excluded_csv_string}')")
    print("Finished loading excluded trials!")

    con.close()

load_trials()

def convert_string_to_list(value):
    if isinstance(value, list):
        return value

    if not isinstance(value, str):
        return []

    if len(value) > 100000:
        return []

    try:
        v1 = ast.literal_eval(value)
    except (ValueError, SyntaxError, MemoryError):
        return []

    if isinstance(v1, list):
        return v1
    else:
        return []

def build_trial_conditions():
    trial_conditions = []

    con = duckdb.connect(str(DUCKDB_DATABASE))
    query = """
    SELECT "NCT ID", "condition names"
    FROM trials
    """

    result = con.execute(query).fetchall()

    for trial in result:
        nct_id = trial[0]
        condition_name = trial[1]
        condition_final = convert_string_to_list(condition_name)

        for condition in condition_final:
            trial_conditions.append((nct_id, condition))

    con.execute("""DROP TABLE IF EXISTS trial_conditions;""")

    query2 = """
    CREATE TABLE trial_conditions (
        nct_id VARCHAR,
        condition_name VARCHAR
    );
    """
    con.execute(query2)

    query3 = """
    INSERT INTO trial_conditions (nct_id, condition_name)
    VALUES (?, ?)
    """

    if len(trial_conditions) > 0:
        con.executemany(query3, trial_conditions)

        database_count = con.execute("""SELECT COUNT(*) FROM trial_conditions""").fetchone()[0]

    print(f"Python rows prepared: {len(trial_conditions)}")
    print(f"Database rows inserted: {database_count}")

    sample_rows = con.execute("""SELECT * FROM trial_conditions LIMIT 5""").fetchall()

    print(sample_rows)

    con.close()

build_trial_conditions()

def build_trial_countries():
    trial_countries = []

    con = duckdb.connect(str(DUCKDB_DATABASE))
    query = """
    SELECT "NCT ID", "countries"
    FROM trials
    """

    result = con.execute(query).fetchall()

    for trial in result:
        nct_id = trial[0]
        country_name = trial[1]
        country_final = convert_string_to_list(country_name)
        country_final = list(set(country_final))

        for country in country_final:
            trial_countries.append((nct_id, country))

    con.execute("""DROP TABLE IF EXISTS trial_countries;""")

    query2 = """
    CREATE TABLE trial_countries (
        nct_id VARCHAR,
        country_name VARCHAR
    );
    """
    con.execute(query2)

    query3 = """
    INSERT INTO trial_countries (nct_id, country_name)
    VALUES (?, ?)
    """

    if len(trial_countries) > 0:
        con.executemany(query3, trial_countries)

    database_count = con.execute("""SELECT COUNT(*) FROM trial_countries""").fetchone()[0]

    print(f"Python rows prepared: {len(trial_countries)}")
    print(f"Database rows inserted: {database_count}")

    sample_rows = con.execute("""SELECT * FROM trial_countries LIMIT 5""").fetchall()

    print(sample_rows)

    con.close()

build_trial_countries()

def build_trial_interventions():
    trial_interventions = []

    con = duckdb.connect(str(DUCKDB_DATABASE))
    query = """
    SELECT "NCT ID", "intervention names", "intervention types"
    FROM trials
    """

    result = con.execute(query).fetchall()

    for trial in result:
        nct_id = trial[0]
        intervention_name = trial[1]
        intervention_type = trial[2]

        intervention_name_final = convert_string_to_list(intervention_name)
        intervention_type_final = convert_string_to_list(intervention_type)

        for index, intervention in enumerate(intervention_name_final):
            if index < len(intervention_type_final):
                intervention_type_value = intervention_type_final[index]
            else:
                intervention_type_value = None

            trial_interventions.append((nct_id, intervention, intervention_type_value))

    con.execute("""DROP TABLE IF EXISTS trial_interventions;""")

    query2 = """
    CREATE TABLE trial_interventions (
        nct_id VARCHAR,
        intervention_name VARCHAR,
        intervention_type VARCHAR
    );
    """
    con.execute(query2)

    query3 = """
    INSERT INTO trial_interventions (nct_id, intervention_name, intervention_type)
    VALUES (?, ?, ?)
    """

    if len(trial_interventions) > 0:
        con.executemany(query3, trial_interventions)

    database_count = con.execute("""SELECT COUNT(*) FROM trial_interventions""").fetchone()[0]

    print(f"Python rows prepared: {len(trial_interventions)}")
    print(f"Database rows inserted: {database_count}")

    sample_rows = con.execute("""SELECT * FROM trial_interventions LIMIT 5""").fetchall()

    print(sample_rows)

    con.close()

build_trial_interventions()

def build_benchmark_results():
    con = duckdb.connect(str(DUCKDB_DATABASE))

    con.execute("""DROP TABLE IF EXISTS benchmark_results;""")

    query = """
    CREATE TABLE benchmark_results (
        condition_name VARCHAR,
        trial_count INTEGER,
        sweep_line_runtime DOUBLE,
        brute_force_runtime DOUBLE,
        speedup DOUBLE,
        results_match BOOLEAN,
        benchmark_date TIMESTAMP
    );
    """
    con.execute(query)

    print("Empty benchmark_results table created")

    sample_rows = con.execute("""SELECT * FROM benchmark_results LIMIT 5""").fetchall()

    print(sample_rows)

    con.close()

build_benchmark_results()

def build_monthly_density():
    con = duckdb.connect(str(DUCKDB_DATABASE))

    con.execute("""DROP TABLE IF EXISTS monthly_density;""")

    query = """
    CREATE TABLE monthly_density (
        month VARCHAR,
        stratum_type VARCHAR,
        condition_query VARCHAR,
        phase_bucket VARCHAR,
        country VARCHAR,
        intervention_type VARCHAR,
        active_trial_count INTEGER,
        started_trials INTEGER,
        ended_trials INTEGER,
        trial_count_total INTEGER,
        group_analyzed BOOLEAN,
        skip_reason VARCHAR
    );
    """
    con.execute(query)

    print("Empty monthly_density table created")

    sample_rows = con.execute("""SELECT * FROM monthly_density LIMIT 5""").fetchall()

    print(sample_rows)

    con.close()

build_monthly_density()

con = duckdb.connect(str(DUCKDB_DATABASE))

tables = con.sql("SHOW TABLES").fetchall()
print(tables)

con.close()