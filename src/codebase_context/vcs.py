# src/codebase_context/vcs.py
"""
Minimal Git/VCS utilities used by codebase_context.core.

Only two public symbols are required right now:

* `is_git_url(url: str) -> bool`
* `RepoCache.clone(url) -> pathlib.Path`
    plus the class-method `RepoCache.cleanup_all()` which `core.py`
    registers via `atexit`.
"""
from __future__ import annotations

import shutil
import stat
import tempfile
from pathlib import Path
from typing import List

try:
    import git  # GitPython
except ImportError:  # pragma: no cover
    raise ImportError(
        "The 'gitpython' package is required for repository cloning. "
        "Install it with: pip install gitpython"
    ) from None

__all__ = ["is_git_url", "RepoCache"]


def is_git_url(url: str) -> bool:
    """Return True for plain GitHub HTTPS URLs.

    Feel free to extend this to SSH or other hosts later.
    """
    return url.startswith("https://github.com/")


class RepoCache:
    """Cache of *temporary* cloned repositories.

    `clone()` downloads the repo into a unique temp dir, remembers the
    directory, and returns its *Path* so callers can work with it.

    At interpreter exit `cleanup_all()` removes every cached dir (see
    registration in `core.py`).
    """

    _cloned: List[Path] = []

    @classmethod
    def clone(cls, url: str) -> Path:
        tempdir = Path(
            tempfile.mkdtemp(prefix=f"codebase_context_{Path(url).stem}_")
        ).resolve()

        # shallow clone speeds things up; adjust as needed
        git.Repo.clone_from(url, tempdir, depth=1)
        cls._cloned.append(tempdir)
        return tempdir, Path(url).stem

    # -------------------------------------------------------------------------
    @classmethod
    def cleanup_all(cls) -> None:  # pragma: no cover
        for path in cls._cloned:
            try:
                shutil.rmtree(
                    path,
                    onerror=lambda fn, p, __: (stat.S_IWRITE, fn(p)),
                )
            except Exception:  # noqa: BLE001
                # Best-effort: log or ignore; we don’t want to raise at exit.
                pass
        cls._cloned.clear()
