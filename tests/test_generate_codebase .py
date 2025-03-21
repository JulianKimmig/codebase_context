import os
from pathlib import Path
import pytest
from codebase_context import generate_codebase


def test_generate_codebase(tmp_path):
    # Create a dummy module directory
    module_dir = tmp_path / "dummy_module"
    module_dir.mkdir()

    # Create a sample Python file inside the dummy module
    sample_file = module_dir / "sample.py"
    sample_file.write_text("print('Hello, pytest!')")

    # Define the expected output file path
    outfile = module_dir / "dummy_module_codebase.txt"

    # Run the codebase generation, forcing overwrite to avoid interactive prompt
    generate_codebase(
        str(module_dir), outfile=str(outfile), endings=[".py"], overwrite=True
    )

    # Verify that the output file was created
    assert outfile.exists(), "Output file was not created."

    # Read the content of the output file
    content = outfile.read_text()

    # Check that the folder tree includes the dummy module name
    assert (
        "dummy_module" in content
    ), "The output does not contain the module folder name."

    # Check that the sample file and its content appear in the output
    assert "sample.py" in content, "The output does not include the sample file."
    assert (
        "print('Hello, pytest!')" in content
    ), "The sample file content is missing from the output."
