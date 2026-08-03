# Database builder
# This script creates the local DuckDB database and loads the project's processed data

from pathlib import Path
import duckdb
import ast

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

def load_trials():
    if not CLEANED_TRIALS_CSV.exists():
        raise FileNotFoundError(f"Cleaned trials file was not found: {CLEANED_TRIALS_CSV}")

    if not EXCLUDED_TRIALS_CSV.exists():
        raise FileNotFoundError(f"Excluded trials file was not found: {EXCLUDED_TRIALS_CSV}")
    
    con = connect_to_database()

    cleaned_csv_string = CLEANED_TRIALS_CSV.as_posix()
    excluded_csv_string = EXCLUDED_TRIALS_CSV.as_posix()

    con.execute(f"CREATE OR REPLACE TABLE trials AS SELECT * FROM read_csv_auto('{cleaned_csv_string}', header=True)")
    print("Finished loading cleaned trials")

    con.execute(f"CREATE OR REPLACE TABLE excluded_trials AS SELECT * FROM read_csv_auto('{excluded_csv_string}', header=True)")
    print("Finished loading excluded trials")

    con.close()

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

    con = connect_to_database()
    query = """
    SELECT "NCT ID", "condition names"
    FROM trials
    """

    result = con.execute(query).fetchall()

    for trial in result:
        nct_id = trial[0]
        condition_name = trial[1]
        condition_final = convert_string_to_list(condition_name)
        condition_final = list(dict.fromkeys(condition_final))

        for condition in condition_final:
            if condition:
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

def build_trial_countries():
    trial_countries = []

    con = connect_to_database()
    query = """
    SELECT "NCT ID", "countries"
    FROM trials
    """

    result = con.execute(query).fetchall()

    for trial in result:
        nct_id = trial[0]
        country_name = trial[1]
        country_final = convert_string_to_list(country_name)
        country_final = list(dict.fromkeys(country_final))

        for country in country_final:
            if country:
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

def build_trial_interventions():
    trial_interventions = []

    con = connect_to_database()
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
                
            if intervention:
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

def build_benchmark_results():
    con = connect_to_database()

    con.execute("""DROP TABLE IF EXISTS benchmark_results;""")

    query = """
    CREATE TABLE benchmark_results (
        condition VARCHAR,
        trial_count INTEGER,
        sweep_line_runtime DOUBLE,
        brute_force_runtime DOUBLE,
        speedup DOUBLE,
        outputs_match BOOLEAN,
    );
    """
    con.execute(query)

    print("Empty benchmark_results table created")

    sample_rows = con.execute("""SELECT * FROM benchmark_results LIMIT 5""").fetchall()

    print(sample_rows)

    con.close()

def build_monthly_density():
    con = connect_to_database()

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

def build_database():
    print("Starting database build...")

    load_trials()
    build_trial_conditions()
    build_trial_countries()
    build_trial_interventions()
    build_benchmark_results()
    build_monthly_density()

    con = connect_to_database()

    tables = con.sql("SHOW TABLES").fetchall()
    print(f"Database tables: {tables}")

    con.close()

    print(f"Database build completed: {DUCKDB_DATABASE}")

if __name__ == "__main__":
    build_database()