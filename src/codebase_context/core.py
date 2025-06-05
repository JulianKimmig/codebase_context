from __future__ import annotations

import logging
from pathlib import Path
from typing import Sequence, Optional, Tuple, TextIO
import os
import shutil

from .config import Config, load_or_create_config, load_config
from .filesystem import (
    build_folder_tree,
    normalize_endings,
    resolve_ignored_paths,
)
from .vcs import RepoCache, is_git_url

_LOG = logging.getLogger(__name__)


class CodebaseGenerationError(RuntimeError):
    """Raised for unrecoverable generation errors."""


class CodebaseGenerator:
    """Generate a self-contained text snapshot of a Python (sub)codebase.

    Example
    -------
    >>> gen = CodebaseGenerator.create("my_pkg")
    >>> outfile = gen.write(overwrite=True)
    >>> print(f"Wrote snapshot to {outfile}")
    """

    def __init__(
        self,
        start_folder: Path,
        endings: Sequence[str],
        config: Config,
        subdirs: Sequence[Path],
        target_folder: Optional[Path] = None,
        basename: Optional[str] = None,
    ) -> None:
        self.start_folder = Path(start_folder).resolve()
        self.endings = tuple(normalize_endings(endings))
        self.config = config
        self.subdirs = tuple(subdirs)
        if target_folder is None:
            target_folder = start_folder
        self.target_folder = Path(target_folder).resolve()
        if basename is None:
            basename = self.start_folder.name
        self.basename = basename

        self._ignored_cache: Optional[Tuple[set[Path], set[Path]]] = None

    # ---------- factory helpers --------------------------------------------------

    @classmethod
    def create(
        cls,
        module_or_path: str | Path | None = None,
        *,
        endings: Optional[Sequence[str]] = None,
        config_path: str | Path | None = None,
        subdirs: Sequence[str | Path] | None = None,
    ) -> "CodebaseGenerator":
        """Return a fully initialised generator, cloning git URLs if needed."""
        tempdir: Path | None = None
        if module_or_path is None and config_path is None:
            raise ValueError("Either module_or_path or config_path must be provided.")
        if module_or_path is None:
            config = load_config(Path(config_path))
            module_or_path = config.get("data", "path", default=None)
            if module_or_path is None:
                raise ValueError("`path` not found in config file.")

        try:
            path: Path
            if is_git_url(str(module_or_path)):
                tempdir, basename = RepoCache.clone(module_or_path)
                path = tempdir
                target_folder = Path(os.getcwd()).resolve()
            else:
                # importlib is safer for module exports, but pathlib Path for dirs
                path = Path(module_or_path).resolve()
                if path.is_file():  # module file → its parent package
                    path = path.parent
                basename = path.name
                target_folder = path

            config = load_or_create_config(
                Path(config_path)
                if config_path
                else target_folder / f"{basename}_generate_codebase.yaml"
            )

            config.set("data", "path", str(module_or_path))

            _LOG.info("Loading config from %s", config.config_path)
            if subdirs is not None:  # pull default from config if not provided
                config.set("filter", "subdirs", list(subdirs))
            subdirs = config.get("filter", "subdirs", default=[""])

            if endings is None:
                endings = config.get("filter", "endings", default=[".py"])

            endings = normalize_endings(endings)
            config.set("filter", "endings", endings)

            return cls(
                start_folder=path,
                endings=endings,
                config=config,
                subdirs=[path / sd for sd in subdirs],
                target_folder=target_folder,
                basename=basename,
            )
        except Exception as exc:
            raise CodebaseGenerationError(str(exc)) from exc
        finally:
            # tempdir cleaned later by RepoCache.cleanup_all()
            pass

    # ---------- public API -------------------------------------------------------

    # ---------- convenience ------------------------------------------------------

    def _get_ignored(self) -> Tuple[set[Path], set[Path]]:
        """Cache and return (ignored_dirs, ignored_files)."""
        if self._ignored_cache is None:
            dirs, files = resolve_ignored_paths(
                self.start_folder,
                self.config.ignore_patterns,
                self.config.ignore_hidden,
            )
            self._ignored_cache = (dirs, files)
        return self._ignored_cache

    def _write(self, out: TextIO) -> None:
        # stream the folder tree

        ignored_dirs, ignored_files = self._get_ignored()

        def is_ignored(p: Path) -> bool:
            return p in ignored_files or any(p.is_relative_to(d) for d in ignored_dirs)

        files, tree = build_folder_tree(
            self.start_folder,
            self.subdirs or [self.start_folder],
            self.endings,
            is_ignored,
        )

        out.write(f"# folder tree:\n\n{tree}\n")
        # stream each file’s header + contents
        for fpath in files:
            if fpath.suffix in self.endings:
                rel = fpath.relative_to(self.start_folder)
                out.write("\n\n# ======================\n")
                out.write(f"# File: {rel}\n")
                out.write("# ======================\n")
                with fpath.open("r", encoding="utf-8", errors="replace") as src:
                    shutil.copyfileobj(src, out)

    def write(
        self,
        outfile: str | Path | None = None,
        *,
        overwrite: bool = False,
    ) -> Path:
        """Stream the snapshot to disk (default `<basename>_codebase.txt`)."""
        if outfile:
            outpath = Path(outfile).expanduser().resolve()
        else:
            outpath = self.target_folder / self.config.get(
                "data",
                "outfile",
                default=f"{self.basename}_codebase.txt",
            )

        if outpath.exists() and not overwrite:
            raise FileExistsError(
                f"{outpath} exists – use overwrite=True or delete it first."
            )

        with outpath.open("w", encoding="utf-8") as out:
            self._write(out)

        _LOG.info("Wrote codebase snapshot to %s", outpath)
        return outpath

    def snapshot(self) -> str:
        """(Deprecated) build full snapshot in memory—modern users should use `.write()`."""
        from warnings import warn

        warn(
            "`snapshot()` builds everything in RAM; use `.write()` instead", UserWarning
        )
        return "".join(self.write().read_text(encoding="utf-8"))

    # ---------- dunder helpers ---------------------------------------------------

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"{self.__class__.__name__}("
            f"start_folder={self.start_folder!s}, endings={self.endings})"
        )


# ensure all temp dirs are cleared at interpreter exit
import atexit  # noqa: E402

atexit.register(RepoCache.cleanup_all)
