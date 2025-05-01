from __future__ import annotations
import os
from pathlib import Path
from typing import Callable, List, Sequence, Tuple

__all__ = ["normalize_endings", "resolve_ignored_paths", "build_folder_tree"]


def normalize_endings(endings: Sequence[str], suffix_only=False) -> List[str]:
    norm_end = [e if e.startswith(".") else f".{e}" for e in endings]
    if suffix_only:
        norm_end = [e[1:] for e in norm_end]
    return norm_end


def resolve_ignored_paths(
    start: Path,
    patterns: List[str],
    ignore_hidden: bool = True,
) -> Tuple[set[Path], set[Path]]:
    import glob

    ignored, include = set(), set()
    if ignore_hidden:
        patterns = patterns + ["**/.*", ".*"]

    for pattern in patterns:
        target = include if pattern.startswith("!") else ignored
        pat = pattern.lstrip("!/")
        matches = glob.glob(str(start / pat), recursive=True)
        for m in matches:
            p = Path(m).resolve()
            if p.exists():
                target.add(p)

    ignored -= include
    dirs = {p for p in ignored if p.is_dir()}
    files = {p for p in ignored if p.is_file()}
    return dirs, files


def build_folder_tree(
    start: Path,
    roots: Sequence[Path],
    endings: Sequence[str],
    is_ignored: Callable[[Path], bool],
) -> Tuple[List[Path], str]:
    files: list[Path] = []
    tree: dict = {"dirs": {}, "files": []}
    endings = normalize_endings(endings, suffix_only=False)

    def _recurse(path: Path, node: dict):
        with os.scandir(path) as it:
            for entry in it:
                p = Path(entry.path)
                if is_ignored(p):
                    continue
                if entry.is_dir(follow_symlinks=False):
                    subtree = node["dirs"].setdefault(
                        entry.name, {"dirs": {}, "files": []}
                    )
                    _recurse(p, subtree)
                elif entry.is_file(follow_symlinks=False):
                    node["files"].append(entry.name)
                    if any(
                        p.suffix == e for e in endings
                    ):  # read only if ending matches
                        files.append(p)

    for root in roots:
        relative_path = root.relative_to(start)
        parts = relative_path.parts
        rtree = tree
        for part in parts:
            rtree = rtree["dirs"].setdefault(part, {"dirs": {}, "files": []})
        _recurse(root, rtree)

    def _stringify(node: dict, lvl: int = 0) -> str:
        lines = []
        for d in sorted(node["dirs"]):
            lines.append("  " * lvl + f"- {d}")
            lines.append(_stringify(node["dirs"][d], lvl + 1))
        for f in sorted(node["files"]):
            lines.append("  " * lvl + f"- {f}")
        return "\n".join(lines)

    tree_str = f"-{start.name}\n{_stringify(tree, 1)}"
    return files, tree_str
