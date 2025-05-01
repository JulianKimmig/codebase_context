"""
Entry-point for  `python -m codebase_context`.

Simply forwards to the Click CLI defined in *codebase_context.cli*.
"""

from __future__ import annotations

from .cli import main

if __name__ == "__main__":  # pragma: no cover
    # Click's `main()` handles sys.argv parsing and exit codes.
    main()
