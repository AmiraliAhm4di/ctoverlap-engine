# Command line interface
# This script reads the commands typed in terminal and routes it to the correct project task

import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["download", "clean", "analyze"])
    args = parser.parse_args()

    if args.command == "download":
        print("Running download...")

    elif args.command == "clean":
        print("Running clean...")

    elif args.command == "analyze":
        print("Running analyze...")

    else:
        print("Unrecognized command")