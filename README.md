# Codebase Context Generator

The Codebase Context Generator is a tool designed to create a detailed summary of a Python codebase, including a folder tree and the contents of Python files. This summary can serve as input for large language models or for documentation purposes. By generating a structured representation of a codebase, this tool aids in understanding and analyzing the structure and contents of Python projects.

## Features

- **Folder Tree Generation**: Creates a hierarchical representation of the directory structure of a Python module or package.
- **Codebase Summarization**: Collects and summarizes the content of Python files within the specified module or package.
- **Flexible Output**: Generates a text file that contains both the folder tree and the raw content of Python files, making it easy to process further.

## Installation

This project does not require installation of external packages beyond the standard Python library. However, it assumes you have Python 3.6 or later installed on your system.

### Installation via pip

```
pip install codebase_context
```

### Installation from source

1. **Clone the repository:**

```

git clone https://yourrepository/codebase_context.git
cd codebase_context

```

2. **Ensure Python 3.6+ is installed:**

```

python3 --version

```

## Usage

To use the Codebase Context Generator, you can run the script from the command line, specifying the target module and the output file.

### Basic Command

```

python3 -m codebase_context <module> [--outfile <output_file.txt>]

```

- `<module>`: The name of the Python module or package you wish to summarize.
- `<output_file.txt>`: Optional. The name of the file to write the summary to. Defaults to `codebase.txt` if not specified.

### Examples

- **Generate a summary for a module called `example_module`:**

```

python3 -m codebase_context example_module

```

This command will create a `codebase.txt` file in the current directory containing the summary of `example_module`.

- **Generate a summary with a custom output file name:**

```

python3 -m codebase_context example_module --outfile summary.txt

```

This will generate a file named `summary.txt` with the codebase summary.

## Contributing

Contributions to the Codebase Context Generator are welcome! Here's how you can contribute:

1. **Fork the repository**: Click the "Fork" button on the GitHub page to create your own copy of the project.

2. **Create a new branch**: Make a branch for your changes with a descriptive name.

3. **Make your changes**: Add new features or fix bugs.

4. **Write tests**: If possible, add unit tests for your changes to ensure reliability.

5. **Submit a pull request**: Open a pull request from your forked repository to the main project. Describe your changes and why they should be included.

Thank you for considering contributing to the Codebase Context Generator. Your efforts help make this tool more robust and useful for everyone!

```

```
