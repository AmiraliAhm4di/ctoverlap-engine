# Command line interface
# This script reads the commands typed in terminal and routes it to the correct project task

from ctoverlap.download import download_one_condition

import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["download", "clean", "analyze"])
    args = parser.parse_args()

    if args.command == "download":
        download_one_condition()

    elif args.command == "clean":
        print("Running clean...")

    elif args.command == "analyze":
        print("Running analyze...")

    else:
        print("Unrecognized command")