"""
codebase_context.config
-----------------------

Light wrapper around *wrapconfig* that provides the small surface
`core.py` (and friends) rely on, plus a couple of convenience
properties.

If you don’t have *wrapconfig* installed you can
    pip install wrapconfig
or replace it with any other “dict-like” config reader – just keep the
same public API.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, List

import wrapconfig  # external dependency

# ---------------------------------------------------------------------------

_DEFAULT_IGNORE = [
    ".git",
    "/**/__pycache__",
    ".vscode",
    ".venv",
    ".env",
    "*generate_codebase.*",
    "*codebase.txt",
    "*.lock",
]

# ---------------------------------------------------------------------------


class Config:
    """Thin façade over *wrapconfig*’s config object.

    Only the minimal methods / properties used elsewhere in the package
    are exposed.  You can freely extend this class later without
    touching the rest of the code-base.
    """

    # You may want to expose `.path` or similar – feel free to extend.
    def __init__(self, _cfg: "wrapconfig.Config", path) -> None:  # type: ignore
        self._cfg = _cfg
        self._path = path

    # --- proxy -----------------------------------------------------------------
    def get(self, section: str, key: str, *, default: Any | None = None) -> Any:
        return self._cfg.get(section, key, default=default)

    def set(self, section: str, key: str, value: Any) -> None:
        self._cfg.set(section, key, value)

    # --- convenience -----------------------------------------------------------
    @property
    def ignore_patterns(self) -> List[str]:
        ig = self.get("filter", "ignore", default=None)
        if ig is None:
            self.set("filter", "ignore", _DEFAULT_IGNORE)
            ig = self.get("filter", "ignore", default=None)
        return ig

    @property
    def ignore_hidden(self) -> bool:
        ans = self.get("filter", "ignore_hidden", default=None)
        if ans is None:
            self.set("filter", "ignore_hidden", True)
            ans = self.get("filter", "ignore_hidden", default=None)
        return bool(ans)

    @property
    def config_path(self) -> Path:
        return self._path


# ---------------------------------------------------------------------------


def load_or_create_config(
    config_path: str | Path,
    *,
    save_default: bool = True,
) -> Config:
    """Return a ready-to-use `Config` object.

    Creates an on-disk YAML file with sensible defaults the first time
    it is called (unless *save_default* is False).
    """
    cfg = wrapconfig.create_config(
        Path(config_path).expanduser(),
        default_save=save_default,
    )
    return Config(
        cfg,
        Path(config_path).expanduser(),
    )  # wrap & return


__all__ = ["Config", "load_or_create_config"]
