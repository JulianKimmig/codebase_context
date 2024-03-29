import os


def generate_codebase(module: str, outfile="codebase.txt"):
    module = __import__(module)

    # Get the module path and directory
    module_path = module.__file__
    module_dir = os.path.dirname(module_path)

    # Start folder is the absolute path to the module directory
    startfolder = os.path.abspath(module_dir)

    # Walk through all files in the folder
    codebase = []

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
        for file in files:
            if file.endswith(".py"):
                # Open the file and read its contents
                with open(os.path.join(root, file), "r") as f:
                    file_contents = f.read()

                # Write the file header and contents to the output file

                context += f"\n\n# {os.path.join(_root, file)}\n\n"
                context += file_contents

    # Write the codebase context to the output file
    with open(outfile, "w") as f:
        f.write(context)
