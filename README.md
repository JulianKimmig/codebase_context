# Codebase Context

Codebase Context is a simple Python tool that generates a textual representation of your project's codebase. It creates a folder tree view along with the contents of files (by default, Python files) to help you get a quick overview of your project's structure.

## Features

- **Folder Tree Generation:** Builds a visual tree of your project directories.
- **File Content Aggregation:** Appends file contents for files matching specified endings.
- **Customizable Filtering:** Supports configuration for file endings, ignoring hidden files/folders, and more via a YAML config file.
- **Easy to Use:** Run the module directly from the command line with minimal configuration.

## Installation

Install the package using pip:

```bash
pip install codebase-context
```

## Usage

You can run the tool from the command line:

```bash
python -m codebase_context <module> [--outfile <output_file>] [--endings <file_endings>] [--config <config_file>] [--overwrite]
```

For example, to generate a codebase file for a module named my_module:

```bash
python -m codebase_context my_module
```

During execution, if the output file already exists, the script will prompt you to confirm whether to overwrite it. You can bypass this prompt by using the `--overwrite` flag.

## Configuration

By default, the tool looks for a generate_codebase.yaml configuration file in the target module's root directory. This file allows you to customize:

File endings to include (e.g., .py).
Hidden file and directory handling.
Patterns for ignoring specific files or directories.
If no configuration file is provided, default settings are used.

## License

This project is licensed under the MIT License.
