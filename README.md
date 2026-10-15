<div align="center">

# Clinical Trial Overlap Engine

**How many clinical trials overlap in each month?**

[![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![DuckDB](https://img.shields.io/badge/database-DuckDB-FFF000?logo=duckdb&logoColor=black)](https://duckdb.org/)
[![R](https://img.shields.io/badge/reporting-R-276DC3?logo=r&logoColor=white)](https://www.r-project.org/)
[![Data source](https://img.shields.io/badge/data-ClinicalTrials.gov%20API%20v2-1f6feb)](https://clinicaltrials.gov/data-api/api)

</div>

## Overview

At any given moment there are thousands of clinical trials being ran and each starts and ends at different times. I used ClinicalTrials.gov records to count how many overlapped in each month for colorectal cancer, melanoma, and breast cancer.

Python downloads and cleans the records, stores them in DuckDB then calculates monthly overlap with a sweep-line algorithm. The algorithm adds trials in their start month and removes them after their end month. I kept a brute-force version to check that both methods gave the same counts.

R creates the figures and summary tables. The analysis also groups trials by phase, country, and intervention type.

## Results

The saved extraction contains 1,000 records per condition (downloaded on August 2, 2026). Eligible trials have a usable start date and a recorded or derived end date.

### Monthly trial activity

| Condition         | Eligible trials | Peak active trials | Peak month     |
| ----------------- | --------------: | -----------------: | -------------- |
| Melanoma          |             980 |                278 | June 2023      |
| Breast cancer     |             986 |                256 | December 2024  |
| Colorectal cancer |             992 |                243 | September 2024 |

<div align="center">

![Monthly trial activity by cancer condition](outputs/figures/monthly_trial_density_by_condition.png)

</div>

### Sweep-line vs. brute force

Both methods produced identical monthly counts for all three conditions. The sweep-line method was **1.63–2.48 times faster** in the saved run using the same 980–992 eligible trials per condition.

<div align="center">

![Sweep-line and brute-force runtime by cancer condition](outputs/figures/sweep_line_runtime_comparison.png)

</div>

See the [peak summary](outputs/report/peak_density_summary.csv) and [benchmark results](outputs/report/benchmark_summary.csv) for the values behind the figures.

There are other generated figures compare peak activity by [phase](outputs/figures/peak_trial_density_by_phase.png), [country](outputs/figures/top_countries_by_peak_trial_density.png), and [intervention type](outputs/figures/top_intervention_types_by_peak_density.png).

## Installation

Requires Python 3.10 or newer. R is needed only to regenerate the figures and summary tables.

```bash
git clone https://github.com/AmiraliAhm4di/ctoverlap-engine.git
cd ctoverlap-engine
python -m venv .venv
```

Activate the environment using the command for your system:

```bash
# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate
```

Install the project and its test dependencies:

```bash
python -m pip install -e ".[dev]"
```

For the R figures, make sure `Rscript` is on your system `PATH` and install:

```bash
Rscript -e "install.packages(c('dplyr','ggplot2','here','readr'), repos='https://cloud.r-project.org')"
```

## Usage

Run commands from the repository root. Exported tables are included so you can recreate the figures and summaries without downloading new records:

```bash
ctoverlap report
```

Figures are saved in `outputs/figures/` and summary tables in `outputs/report/`.

<details>
<summary><strong>Rebuild the analysis from ClinicalTrials.gov</strong></summary>

Run these steps in order. Downloading again replaces the local raw records and the later steps update the outputs:

```bash
ctoverlap download
ctoverlap clean
ctoverlap build-db
ctoverlap analyze
ctoverlap benchmark
ctoverlap export
ctoverlap report
```

Records can change between downloads so a new run may give different counts.

</details>

Run the tests with:

```bash
python -m pytest
```

Tests cover date handling, phase groups, interval rules, downloads, and agreement between the two overlap methods.

## Limitations

Results cover up to 1,000 records per condition. Activity is inferred from trial dates which includes ones that are scheduled for future dates. The reported speedups come from a single benchmark run.

## Why I built this

After my first project in R, I wanted to get more comfortable with Python. I chose clinical trial data because counting overlapping trials gave me a reason to work with real data and write an algorithm myself.

## Contact

[@AmiraliAhm4di](https://github.com/AmiraliAhm4di)
