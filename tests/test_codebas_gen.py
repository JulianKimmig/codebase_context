import unittest
from unittest.mock import patch, mock_open
import os
import sys
import tempfile
from codebase_context import generate_codebase


class TestGenerateCodebase(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.test_module_name = "testmodule"
        self.test_module_path = os.path.join(self.temp_dir.name, self.test_module_name)
        sys.path.append(self.temp_dir.name)
        os.makedirs(self.test_module_path)

        # Create a test file within the module
        self.test_file_name = "__init__.py"
        with open(os.path.join(self.test_module_path, self.test_file_name), "w") as f:
            f.write("# Test file content")

    @patch("builtins.open", new_callable=mock_open)
    def test_generate_codebase_success(self, mock_file):
        generate_codebase(
            self.test_module_name,
            outfile=os.path.join(self.temp_dir.name, "codebase.txt"),
        )

        # Check if the output file was attempted to be written
        mock_file.assert_called_with(
            os.path.join(self.temp_dir.name, "codebase.txt"), "w"
        )

        # The test here is minimal due to mocking; ideally, inspect the content written to mock_file for correctness

    def test_module_not_found(self):
        with self.assertRaises(ModuleNotFoundError):
            generate_codebase("nonexistentmodule")

    def test_output_structure(self):
        # This test would ideally check the structure of the output file to ensure it matches the expected folder tree
        # Since we're working in a temporary directory, this would involve actually running generate_codebase and inspecting the output
        outfile = os.path.join(self.temp_dir.name, "codebase.txt")
        generate_codebase(self.test_module_name, outfile=outfile)

        with open(outfile, "r") as f:
            content = f.read()

        # Validate content structure
        # This is a basic validation; you should expand it to ensure the content matches the expected structure precisely
        self.assertIn("# folder tree:", content)
        self.assertIn(f"{self.test_module_name}", content)
        self.assertIn(f"- {self.test_file_name}", content)

        self.assertIn("# __init__.py", content)

        self.assertIn("# Test file content", content)
