import argparse
import os
from . import generate_codebase


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("module", type=str)
    parser.add_argument("--outfile", type=str, default="codebase.txt")
    args = parser.parse_args()

    if os.path.exists(args.outfile):
        print(f"Output file {args.outfile} already exists")
        replace = input("Do you want to replace it? (y/n): ")
        if replace.lower() != "y":
            print("Exiting...")
            return

    # Run the main function
    generate_codebase(args.module, args.outfile)


if __name__ == "__main__":
    main()
