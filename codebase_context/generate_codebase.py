import os
import wrapconfig
from wrapconfig._read import create_config

wrapconfig.create_config = create_config


def generate_codebase(
    module: str,
    outfile="codebase.txt",
    endings=[".py"],
    config=None,
    ignore_hidden=None,
):
    """
    Generates a codebase file for the given module.

    Args:
      module (str): The name of the module to generate the codebase for.
      outfile (str): The name of the output file to write the codebase to. Defaults to "codebase.txt".

    Raises:
      ModuleNotFoundError: If the given module cannot be found.

    Returns:
      None
    """

    if config is None:
        config = "generate_codebase.toml"

    config = wrapconfig.create_config(config, default_save=True)

    endings = [e if e.startswith(".") else "." + e for e in endings]
    if endings:
        config.set(
            "filter",
            "endings",
            list(set(config.get("filter", "endings", default=[]) + endings)),
        )

    endings = config.get("filter", "endings", default=[])
    if ignore_hidden is None:
        ignore_hidden = config.get("filter", "ignore_hidden", default=True)
    config.set("filter", "ignore_hidden", ignore_hidden)

    ignored_paths = config.get(
        "filter",
        "ignore",
        default=[".git", "/**/__pycache__", ".vscode", ".venv", ".env", ""],
    )
    config.set("filter", "ignored_paths", ignored_paths)

    if not os.path.isdir(module):
        try:
            module = __import__(module)

            # Get the module path and directory
            module_path = module.__file__
            module_dir = os.path.dirname(module_path)
        except ModuleNotFoundError:
            module_dir = module
            if not os.path.exists(module_dir) or not os.path.isdir(module_dir):
                raise
    else:
        module_dir = module
    # Start folder is the absolute path to the module directory
    startfolder = os.path.abspath(module_dir)

    # Walk through all files in the folder

    def build_folder_tree(startfolder: str) -> str:
        """Builds a folder tree representation of the given startfolder.

        Ignores any folders/files starting with '__pycache__'.
        """

        folder_tree = {
            "dirs": {},  # Subdirectories
            "files": [],  # Files in this directory
        }

        for root, dirs, files in os.walk(startfolder):
            # Replace the startfolder path with an empty string
            _root = root.replace(startfolder, "").strip(os.sep)

            # Ignore '__pycache__' folders
            if "__pycache__" in _root:
                continue

            # Split the relative root path into subdirectories
            srotts = _root.split(os.sep)

            # Start with the folder_tree dictionary
            sftree = folder_tree

            # Iterate through the subdirectories
            if _root != "":
                for sroot in srotts:
                    # Create a new subdirectory if it doesn't exist
                    if sroot not in sftree["dirs"]:
                        sftree["dirs"][sroot] = {"dirs": {}, "files": []}

                    # Move down to the next level of the tree
                    sftree = sftree["dirs"][sroot]

            # Add files to the current directory
            for file in files:
                sftree["files"].append(file)

        def string_tree(tree: dict, level: int = 0) -> str:
            """Recursively converts the folder tree to a string representation."""

            tree_str = ""

            # Iterate through the subdirectories
            for d in tree["dirs"]:
                # Add the subdirectory name with indentation
                tree_str += "  " * level + f"- {d}\n"

                # Recursively add the subdirectory's string representation
                tree_str += string_tree(tree["dirs"][d], level + 1)

            # Iterate through the files
            for f in tree["files"]:
                # Add the file name with indentation
                tree_str += "  " * level + f"- {f}\n"

            # Return the string representation of the tree
            return tree_str

        # Create the folder tree string representation
        folder_tree = f"-{os.path.basename(startfolder)}\n" + string_tree(
            folder_tree, 1
        )

        # Return the folder tree string
        return folder_tree

    # Write the folder tree to the output file

    context = "# folder tree:\n\n" + build_folder_tree(startfolder) + "\n"

    # Iterate through the files in the folder and write their contents to the output file
    for root, dirs, files in os.walk(startfolder):
        _root = root.replace(startfolder, "").strip(os.sep)
        if ignore_hidden and any([d.startswith(".") for d in _root.split(os.sep)]):
            continue
        for file in files:
            if ignore_hidden and file.startswith("."):
                continue
            if any([file.endswith(e) for e in endings]):
                # print("including", file)
                # Open the file and read its contents
                with open(os.path.join(root, file), "r") as f:
                    file_contents = f.read()

                # Write the file header and contents to the output file

                context += f"""

# ======================
# File: {os.path.join(_root, file)}
# ======================
"""

                context += file_contents
            else:
                print("excluding", file)
    # Write the codebase context to the output file
    with open(outfile, "w") as f:
        f.write(context)
