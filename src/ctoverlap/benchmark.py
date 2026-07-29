# Benchmarking methods
# This script runs the sweep-line and brute-force overlap methods and measures their execution times

from pathlib import Path
import duckdb
import time
from ctoverlap.sweep_line import sweep_line
from ctoverlap.brute_force import brute_force
from ctoverlap.analyze import convert_intervals

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
DATABASE = PROJECT_ROOT / "data" / "database"
DUCKDB_DATABASE = DATABASE / "clinical_trials.duckdb"
OUTPUT_TABLES = PROJECT_ROOT / "outputs" / "tables"


def get_interval(condition):
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


def benchmark_condition(condition):
    raw_intervals = get_interval(condition)
    converted_intervals = convert_intervals(raw_intervals)
    amount = len(converted_intervals)

    start_time = time.perf_counter()
    maximum_overlap, event_months, sweep_output = sweep_line(converted_intervals)
    end_time = time.perf_counter()
    sweep_runtime = end_time - start_time

    start_time = time.perf_counter()
    brute_output = brute_force(converted_intervals)
    end_time = time.perf_counter()
    brute_runtime = end_time - start_time

    outputs_match = sweep_output == brute_output
    speedup = brute_runtime / sweep_runtime

    result = {
        "condition": condition,
        "trial_count": amount,
        "sweep_line_runtime": sweep_runtime,
        "brute_force_runtime": brute_runtime,
        "speedup": speedup,
        "outputs_match": outputs_match,
    }

    return result


conditions = [
    "colorectal cancer",
    "melanoma",
    "breast cancer",
]

benchmark_results = []

for condition in conditions:
    result = benchmark_condition(condition)
    benchmark_results.append(result)

for result in benchmark_results:
    print(f"""
Condition: {result["condition"]}
Trials tested: {result["trial_count"]}
Sweep-line runtime: {result["sweep_line_runtime"]:.6f} seconds
Brute-force runtime: {result["brute_force_runtime"]:.6f} seconds
Speedup: {result["speedup"]:.2f}x
Outputs match: {result["outputs_match"]}
""")

def save_results(benchmark_results):
    con = duckdb.connect(str(DUCKDB_DATABASE))
    query = ("""
    CREATE TABLE IF NOT EXISTS benchmark_results (
            condition VARCHAR,
            trial_count INTEGER,
            sweep_line_runtime DOUBLE,
            brute_force_runtime DOUBLE,
            speedup DOUBLE,
            outputs_match BOOLEAN
        );
    """)
    query2 = """DROP TABLE IF EXISTS benchmark_results;"""

    con.execute(query2)
    con.execute(query)

    rows = []

    for result in benchmark_results:
        rows.append((
            result["condition"],
            result["trial_count"],
            result["sweep_line_runtime"],
            result["brute_force_runtime"],
            result["speedup"],
            result["outputs_match"],
        ))

    con.executemany("""
        INSERT INTO benchmark_results (
            condition,
            trial_count,
            sweep_line_runtime,
            brute_force_runtime,
            speedup,
            outputs_match
        )
        VALUES (?, ?, ?, ?, ?, ?);
    """, rows)

    con.close()


def export_benchmark_results():
    OUTPUT_TABLES.mkdir(parents=True, exist_ok=True)
    output_file = OUTPUT_TABLES / "benchmark_results.csv"

    con = duckdb.connect(str(DUCKDB_DATABASE))

    con.execute(f"""
        COPY benchmark_results
        TO '{output_file.as_posix()}'
        (HEADER, DELIMITER ',');
    """)

    con.close()


save_results(benchmark_results)
export_benchmark_results()

print("Benchmark results saved to DuckDB and exported to CSV.")