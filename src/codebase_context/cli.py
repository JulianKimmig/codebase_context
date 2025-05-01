import logging
import sys
from pathlib import Path
from typing import Optional
import click

from codebase_context import generate_codebase, CodebaseGenerationError

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("module", metavar="MODULE|PATH")
@click.option("--outfile", type=click.Path(path_type=Path), help="Destination file.")
@click.option(
    "--endings", multiple=True, required=False, help="File endings to include."
)
@click.option("--config-path", type=click.Path(path_type=Path))
@click.option("--subdirs", "subdirs", multiple=True, help="Restrict to sub-folder(s).")
@click.option("--overwrite", is_flag=True, help="Overwrite existing outfile.")
def main(
    module: str,
    outfile: Path | None,
    endings: Optional[tuple[str, ...]],
    config_path: Path | None,
    subdirs: tuple[str, ...],
    overwrite: bool,
) -> None:
    """Generate a text snapshot of a codebase."""
    try:
        generate_codebase(
            module,
            outfile=outfile,
            endings=endings,
            config_path=config_path,
            subdirs=subdirs or None,
            overwrite=overwrite,
        )
    except (FileExistsError, CodebaseGenerationError) as exc:
        _ = click.secho(str(exc), fg="red", err=True)
        sys.exit(1)
