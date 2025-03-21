import os
import fnmatch
import wrapconfig
import glob
from wrapconfig._read import create_config

wrapconfig.create_config = create_config


def generate_codebase(
    module: str,
    outfile=None,
    endings=[".py"],
    config=None,
    ignore_hidden=None,
    save_config=True,
    overwrite=False,
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

    # Determine the module directory
    if not os.path.isdir(module):
        try:
            module_obj = __import__(module)
            module_path = module_obj.__file__
            module_dir = os.path.dirname(module_path)
        except ModuleNotFoundError:
            module_dir = module
            if not os.path.exists(module_dir) or not os.path.isdir(module_dir):
                raise
    else:
        module_dir = module

    startfolder = os.path.abspath(module_dir)

    if config is None:
        config = os.path.join(startfolder, "generate_codebase.yaml")
    if outfile is None:
        outfile = os.path.join(
            startfolder, f"{os.path.basename(startfolder)}_codebase.txt"
        )

    if os.path.exists(outfile) and not overwrite:
        print(f"Output file {outfile} already exists")
        replace = input("Do you want to replace it? (y/n): ")
        if replace.lower() != "y":
            print("Exiting...")
            return
    config = wrapconfig.create_config(config, default_save=save_config)

    # Normalize file endings and update the configuration
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

    # Get the ignore list from config; note the default contains some common folders.
    ignored_paths = config.get(
        "filter",
        "ignore",
        default=[
            ".git",
            "/**/__pycache__",
            ".vscode",
            ".venv",
            ".env",
            "generate_codebase.*",
            "*codebase.txt",
            "*.lock",
        ],
    )
    config.set("filter", "ignore", ignored_paths)

    # Start folder is the absolute path to the module directory

    if ignore_hidden:
        ignored_paths.append("**/.*")
        ignored_paths.append(".*")
    ignored = set()
    include = set()
    for ipattern in ignored_paths:
        if ipattern.startswith("!"):
            target = include
            ipattern = ipattern[1:]
        else:
            target = ignored

        if ipattern.startswith("/"):
            ipattern = ipattern[1:]

        target.update(
            os.path.abspath(os.path.join(startfolder, p))
            for p in glob.glob(
                ipattern, root_dir=startfolder, recursive=True, include_hidden=True
            )
        )

    ignored = ignored - include

    ignored_directories = set([p for p in ignored if os.path.isdir(p)])
    ignored_files = set([p for p in ignored if os.path.isfile(p)])

    def is_ignored(path: str) -> bool:
        # check if path or any of its parent directories are in the ignored set

        for p in ignored_directories:
            if path.startswith(p):
                return True
        if path in ignored_files:
            return True

        return False

    # print("ignored", ignored)

    files2read = []

    def build_folder_tree(startfolder: str) -> str:
        """Builds a folder tree representation of the given startfolder,
        skipping files and directories that match the ignore list.
        """
        folder_tree = {"dirs": {}, "files": []}

        for root, dirs, files in os.walk(startfolder):
            _root = root.replace(startfolder, "").strip(os.sep)

            # Skip this directory entirely if its relative path is ignored.
            if _root and is_ignored(root):
                continue

            # Filter out hidden directories if required.
            if ignore_hidden:
                dirs[:] = [d for d in dirs if not d.startswith(".")]
            # Remove any subdirectories that match the ignore list.
            dirs[:] = [d for d in dirs if not is_ignored(os.path.join(root, d))]
            # Also filter files based on the ignore list.
            files = [f for f in files if not is_ignored(os.path.join(root, f))]
            files2read.extend([os.path.join(root, f) for f in files])

            # Build the tree structure for the current folder.
            srotts = _root.split(os.sep) if _root else []
            sftree = folder_tree
            for sroot in srotts:
                if sroot not in sftree["dirs"]:
                    sftree["dirs"][sroot] = {"dirs": {}, "files": []}
                sftree = sftree["dirs"][sroot]
            sftree["files"].extend(files)

        def string_tree(tree: dict, level: int = 0) -> str:
            tree_str = ""
            for d in tree["dirs"]:
                tree_str += "  " * level + f"- {d}\n"
                tree_str += string_tree(tree["dirs"][d], level + 1)
            for f in tree["files"]:
                tree_str += "  " * level + f"- {f}\n"
            return tree_str

        folder_tree_str = f"-{os.path.basename(startfolder)}\n" + string_tree(
            folder_tree, 1
        )
        return folder_tree_str

    # Start with the folder tree header.
    context = f"# folder tree:\n\n{build_folder_tree(startfolder)}\n".encode()

    for file in files2read:
        if any(file.endswith(e) for e in endings):
            with open(file, "rb") as f:
                file_contents = f.read()

            context += f"""

# ======================
# File: {file.replace(startfolder, "")}
# ======================
""".encode()

            context += file_contents
        else:
            print("excluding", file.replace(startfolder, ""))

    with open(outfile, "wb") as f:
        f.write(context)
