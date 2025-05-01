import argparse
import os
from . import generate_codebase


def main():
    """
    Runs the main function.

    Args:
      module (str): The name of the module to generate codebase for.
      outfile (str): The name of the output file to write the codebase to.

    Returns:
      None

    Side Effects:
      Writes the generated codebase to the specified output file.

    Examples:
      >>> main("my_module", "codebase.txt")
      Output file codebase.txt already exists
      Do you want to replace it? (y/n): y
      Writing codebase for my_module to codebase.txt...
    """
    # Parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("module", type=str)
    parser.add_argument("--outfile", type=str, default=None)
    parser.add_argument("--endings", type=str, nargs="*", default=["py"])
    parser.add_argument("--config", type=str, default=None)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument(
        "--subdirs",
        type=str,
        nargs="*",
        default=None,
        help="Subdirectories to include in the codebase generation in the format 'subdir1,subdir2'",
    )
    args = parser.parse_args()

    # Run the main function
    generate_codebase(
        args.module,
        args.outfile,
        args.endings,
        configpath=args.config,
        overwrite=args.overwrite,
        subdirs=args.subdirs,
    )


if __name__ == "__main__":
    main()
