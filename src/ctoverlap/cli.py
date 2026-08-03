# Command line interface
# This script reads the commands typed in terminal and routes it to the correct project task

from ctoverlap.download import download_one_condition
from ctoverlap.download import download_all
from ctoverlap.inspect_fields import inspect_fields
from ctoverlap.clean import save_cleaned
from ctoverlap.export import export_all_density
from ctoverlap.report import run_report
from ctoverlap.analyze import load_monthly_density
from ctoverlap.download import SUPPORTED_CONDITIONS
from ctoverlap.database import build_database
from ctoverlap.benchmark import run_benchmarks

import argparse
import sys
import subprocess

def main():
    parser = argparse.ArgumentParser(description="Download, clean, analyze, benchmark and report clinical trial overlap data")
    parser.add_argument("command", choices=[
        "download", 
        "clean", 
        "analyze",
        "inspect-fields",
        "export",
        "report",
        "benchmark",
        "build-db",
        ],
        help="Project task to run,"
        )
    parser.add_argument("condition", nargs="?", default="all", choices=[
        "all",
        "colorectal cancer",
        "melanoma",
        "breast cancer",
    ],
    help="Condition used by download and inspect-fields commands"
    )
    
    args = parser.parse_args()

    if args.command == "download":
        if args.condition == "all":
            print("Downloading all supported conditions...")
            download_all()
        else:
            print(f"Downloading {args.condition}...")
            download_one_condition(args.condition)

    elif args.command == "clean":
        if args.condition != "all":
            parser.error("The clean command processes all supported conditions. Do not provide a condition")
        print("Cleaning trial data...")
        save_cleaned()

    elif args.command == "analyze":
        if args.condition != "all":
            parser.error("The analyze command processes all supported conditions. Do not provide a condition")

        print("Running overlap analysis...")
        load_monthly_density()
        print("Analysis completed.")

    elif args.command == "inspect-fields":
        if args.condition == "all":
            parser.error(
            "inspect-fields requires one condition, such as "
            "'ctoverlap inspect-fields melanoma'."
        )
        print(f"Inspecting {args.condition}...")
        inspect_fields(args.condition)

    elif args.command == "export":
        if args.condition != "all":
            parser.error("The export command exports all analysis groups. Do not provide a condition")

        print("Exporting analysis tables...")
        export_all_density()
        print("Analysis tables exported.")

    elif args.command == "report":
        if args.condition != "all":
            parser.error("The report command does not accept a condition")

        print("Creating the final report...")
        run_report()

    elif args.command == "build-db":
        if args.condition != "all":
            parser.error("The build-db command does not accept a condition")

        build_database()

    elif args.command == "benchmark":
        if args.condition != "all":
            parser.error("The benchmark command currently benchmarks all supported conditions")

        run_benchmarks()

    else:
        print("Unrecognized command")