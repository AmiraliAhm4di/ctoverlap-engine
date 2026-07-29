# Command line interface
# This script reads the commands typed in terminal and routes it to the correct project task

from ctoverlap.download import download_one_condition
from ctoverlap.download import download_all
from ctoverlap.inspect_fields import inspect_fields
from ctoverlap.clean import save_cleaned
from ctoverlap.export import export_all_density

import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=[
        "download", 
        "clean", 
        "analyze",
        "inspect-fields",
        ])
    parser.add_argument("condition", nargs="?", default="all", choices=[
        "all",
        "colorectal cancer",
        "melanoma",
        "breast cancer",
    ])
    
    args = parser.parse_args()

    if args.command == "download":
        if args.condition == "all":
            print("Downloading all supported conditions...")
            download_all()
        elif args.condition == "colorectal cancer":
            print("Downloading colorectal cancer...")
            download_one_condition("colorectal cancer")
        elif args.condition == "melanoma":
            print("Downloading melanoma...")
            download_one_condition("melanoma")
        elif args.condition == "breast cancer": 
            print("Downloading breast cancer...")
            download_one_condition("breast cancer")
        else:
            print("Unsupported Condition, please try again")

    elif args.command == "clean":
        print("Cleaning started...")
        save_cleaned()

    elif args.command == "analyze":
        print("Running analyze...")

    elif args.command == "inspect-fields":
        if args.condition == "all":
            print("Please select a valid condition.")
        elif args.condition == "colorectal cancer":
            print("Inspecting colorectal cancer...")
            inspect_fields("colorectal cancer")
        elif args.condition == "melanoma":
            print("Inspecting melanoma...")
            inspect_fields("melanoma")
        elif args.condition == "breast cancer":
            print("Inspecting breast cancer...")
            inspect_fields("breast cancer")

    elif args.command == "export":
        export_all_density()
        print("Exporting...")

    else:
        print("Unrecognized command")