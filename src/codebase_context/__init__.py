# src/codebase_context/__init__.py
from __future__ import annotations
from pathlib import Path
from typing import Optional, Sequence, Union
from .core import CodebaseGenerator, CodebaseGenerationError


def generate_codebase(
    module: str | Path | None = None,
    *,
    endings: Optional[Sequence[str]] = None,
    config_path: Optional[Union[str, Path]] = None,
    subdirs: Optional[Sequence[Union[str, Path]]] = None,
    outfile: Optional[Union[str, Path]] = None,
    overwrite: bool = False,
):
    gen = CodebaseGenerator.create(
        module_or_path=module,
        endings=endings or None,
        config_path=config_path,
        subdirs=subdirs,
    )
    path = gen.write(outfile=outfile, overwrite=overwrite)
    return path


__all__ = ["CodebaseGenerator", "CodebaseGenerationError"]
