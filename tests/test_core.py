import os
import shutil
from io import StringIO
from pathlib import Path
import pytest

from codebase_context import generate_codebase
from codebase_context.core import CodebaseGenerator, CodebaseGenerationError
from codebase_context.filesystem import (
    build_folder_tree,
    resolve_ignored_paths,
    normalize_endings,
)


def create_sample_structure(tmp_path: Path):
    # Set up a nested directory with files
    root = tmp_path / "root"
    sub1 = root / "sub1"
    sub2 = root / "sub2"
    sub1.mkdir(parents=True)
    sub2.mkdir(parents=True)
    # files
    (root / "a.py").write_text("print('a')")
    (sub1 / "b.py").write_text("print('b')")
    (sub2 / "c.txt").write_text("text")
    # hidden and ignored
    (root / ".hidden").write_text("secret")
    return root


def test_normalize_endings():
    assert normalize_endings(["py", ".txt"]) == [".py", ".txt"]
    assert normalize_endings([]) == []


def test_resolve_ignored(tmp_path):
    # create files and directories
    f1 = tmp_path / "keep.py"
    f1.write_text("")
    f2 = tmp_path / "ignore.log"
    f2.write_text("")
    dirs, files = resolve_ignored_paths(
        tmp_path, patterns=["*.log", "!*.py"], ignore_hidden=False
    )
    assert f2 in files

    assert f1 not in files


def test_build_folder_tree(tmp_path):
    root = create_sample_structure(tmp_path)

    def no_ignore(p):
        return False

    files, tree = build_folder_tree(
        root, roots=[root], endings=[".py"], is_ignored=no_ignore
    )
    print(files)
    # only .py files are listed
    assert any(f.name == "a.py" for f in files)
    assert any(f.name == "b.py" for f in files)
    assert all(list(f.suffix == ".py" for f in files)), list(f.name for f in files)
    # tree contains sub1 and files
    assert "- sub1" in tree
    assert "- a.py" in tree
    assert "- b.py" in tree


def test_write_and_snapshot(tmp_path):
    root = create_sample_structure(tmp_path)
    gen = CodebaseGenerator.create(root, endings=[".py"], subdirs=[root])
    # test snapshot warning
    snap = gen.snapshot()
    assert "# folder tree:" in snap
    assert "# File: a.py" in snap

    # test write
    outfile = tmp_path / "out.txt"
    path = gen.write(outfile=str(outfile), overwrite=True)
    assert path == outfile
    content = outfile.read_text()
    assert "# folder tree:" in content


def test_write_raises_if_exists(tmp_path):
    root = create_sample_structure(tmp_path)
    gen = CodebaseGenerator.create(root)
    outfile = tmp_path / "duplicate.txt"
    outfile.write_text("")
    with pytest.raises(FileExistsError):
        gen.write(outfile=str(outfile), overwrite=False)


def test_write_stringio(tmp_path):
    root = create_sample_structure(tmp_path)
    gen = CodebaseGenerator.create(root)
    buf = StringIO()
    # use private _write to stream into StringIO
    gen._write(buf)
    txt = buf.getvalue()
    assert "# folder tree:" in txt
    assert "a.py" in txt


def test_generate_codebase_helper(tmp_path):
    root = create_sample_structure(tmp_path)
    outfile = tmp_path / "gen.txt"
    result = generate_codebase(
        str(root), endings=[".py"], outfile=str(outfile), overwrite=True
    )
    assert result == outfile
    assert outfile.exists()


def test_ignore_hidden_by_default(tmp_path):
    root = tmp_path / "pkg"
    root.mkdir()
    (root / "normal.py").write_text("print()")
    (root / ".secret.py").write_text('print("hidden")')
    gen = CodebaseGenerator.create(root)
    buf = StringIO()
    gen._write(buf)
    out = buf.getvalue()
    assert "normal.py" in out
    assert ".secret.py" not in out


def test_subdir_filtering(tmp_path):
    root = create_sample_structure(tmp_path)
    sub1 = root / "sub1"
    gen = CodebaseGenerator.create(root, subdirs=[sub1], endings=[".py"])
    buf = StringIO()
    gen._write(buf)
    out = buf.getvalue()
    # only files under sub1 and root (root is default, but subdirs override)
    assert "b.py" in out
    assert "a.py" not in out  # a.py in root should not appear
