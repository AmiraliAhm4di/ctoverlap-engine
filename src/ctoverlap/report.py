


from pathlib import Path
import shutil
import subprocess


PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPORTS_PATH = PROJECT_ROOT / "reports"
REPORT_SCRIPT = REPORTS_PATH / "final_report.R"


def run_report():
    rscript_path = shutil.which("Rscript")

    if rscript_path is None:
        print("Error: Rscript is not installed or not in your PATH.")
        return

    if not REPORT_SCRIPT.exists():
        print(f"Error: Report script was not found at {REPORT_SCRIPT}")
        return
    try:
        subprocess.run(
            [rscript_path, str(REPORT_SCRIPT)], cwd=PROJECT_ROOT, check=True
            )

    except subprocess.CalledProcessError:
        print("Error: The R report failed.")
        return

    print("Report created successfully.")
    