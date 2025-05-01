import os
import fnmatch
import wrapconfig
import glob
import git
from wrapconfig._read import create_config
import tempfile
import shutil
import re
import stat
from typing import Optional,List,Union

wrapconfig.create_config = create_config


def is_git_url(url: str) -> bool:
    return re.match(r"^https?://(www\.)?github\.com/.+/.+(\.git)?$", url) is not None


def clone_repo(url: str, tmpdir: str) -> str:
    if git is None:
        raise ImportError("GitPython is required for cloning. Install with: pip install gitpython")
    repo = git.Repo.clone_from(url, tmpdir)
    repodir = repo.working_tree_dir
    if not os.path.isdir(repodir):
        raise ValueError(f"Invalid repository URL: {url}")
    if not os.path.exists(repodir):
        raise ValueError(f"Repository not found: {url}")
    
    repo.close()
    return repodir

def generate_codebase(
    module: str,
    outfile=None,
    endings=[".py"],
    configpath=None,
    ignore_hidden=None,
    save_config=True,
    overwrite=False,
    subdirs:Optional[Union[str,List[str]]]=None,
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

    tempdir = None
    try:
        if is_git_url(module):
            # create a temporary directory to clone the repo the name of the temp dir should be the name of the repo
            # remponame is the name of the repo without the any extension or url parameters
            
            reponame =  os.path.basename(module)
            tempdir = tempfile.mkdtemp(prefix="codebase_context_"+reponame+"_")
            module_dir = clone_repo(module, tempdir)
            # in guthub outfile is in the root of the repo
            outfile = os.path.join(os.getcwd(), f"{os.path.basename(module)}_codebase.txt")
            configpath = os.path.join(os.getcwd(), f"{os.path.basename(module)}_generate_codebase.yaml")
        else:
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
        
        if configpath is None:
            configpath = os.path.join(startfolder, "generate_codebase.yaml")
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
        config = wrapconfig.create_config(configpath, default_save=save_config)

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
        if subdirs is not None:
            if isinstance(subdirs, str):
                subdirs = [subdirs]
            # Convert subdir paths to absolute paths
            
            config.set("filter", "subdirs", subdirs)
            subdirs = [os.path.abspath(os.path.join(startfolder, sd)) for sd in subdirs]
        else:

            subdirs = config.get(
                "filter", "subdirs", default=[""]
            )
            subdirs = [os.path.abspath(os.path.join(startfolder, sd)) for sd in subdirs]
            

        files2read = []

    
        def build_folder_tree(filtered_startfolders: List[str]) -> str:
            """Builds a folder tree for the given subdirectories."""
            folder_tree = {"dirs": {}, "files": []}

            for start in filtered_startfolders:
                for root, dirs, files in os.walk(start):
                    # Skip ignored directories
                    if is_ignored(root):
                        continue

                    rel_root = os.path.relpath(root, startfolder)
                    rel_root = "" if rel_root == "." else rel_root

                    # Filter dirs
                    if ignore_hidden:
                        dirs[:] = [d for d in dirs if not d.startswith(".")]
                    dirs[:] = [d for d in dirs if not is_ignored(os.path.join(root, d))]
                    files = [f for f in files if not is_ignored(os.path.join(root, f))]

                    files2read.extend([os.path.join(root, f) for f in files])

                    # Build folder tree dict
                    parts = rel_root.split(os.sep) if rel_root else []
                    subtree = folder_tree
                    for part in parts:
                        subtree = subtree["dirs"].setdefault(part, {"dirs": {}, "files": []})
                    subtree["files"].extend(files)

            def string_tree(tree: dict, level: int = 0) -> str:
                tree_str = ""
                for d in sorted(tree["dirs"]):
                    tree_str += "  " * level + f"- {d}\n"
                    tree_str += string_tree(tree["dirs"][d], level + 1)
                for f in sorted(tree["files"]):
                    tree_str += "  " * level + f"- {f}\n"
                return tree_str

            return f"-{os.path.basename(startfolder)}\n" + string_tree(folder_tree, 1)

        # Start with the folder tree header.
        context = f"# folder tree:\n\n{build_folder_tree(subdirs)}\n".encode()

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
    finally:
        if tempdir:
            try: 
                def on_rm_error(func, path, exc_info):
                    # path may be read-only, so make it writable and try again
                    os.chmod(path, stat.S_IWRITE)
                    func(path)
                    
                shutil.rmtree(tempdir, onerror=on_rm_error)
            except Exception as e:
                print(f"Error removing tempdir {tempdir}: {e}")