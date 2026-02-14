"""OSP CLI - Transform seeds into living AI workspaces.

Usage:
    osp init --seed tabula_rasa
    osp list
    osp preview --seed glitch
    osp validate seeds/my_seed.yaml
"""

from __future__ import annotations

from pathlib import Path

import click

from osp import __version__
from osp.generator import (
    SEEDS_DIR,
    init_workspace,
    list_available_seeds,
    preview_file,
    resolve_seed_path,
)
from osp.validator import validate_file


@click.group()
@click.version_option(version=__version__, prog_name="osp")
def main() -> None:
    """Open Soul Protocol CLI - Give your AI agent a soul."""


@main.command()
@click.option("--seed", required=True, help="Seed name or path to YAML file.")
@click.option(
    "--workspace",
    default="./workspace",
    type=click.Path(),
    help="Output directory for generated workspace.",
)
def init(seed: str, workspace: str) -> None:
    """Generate an OpenClaw workspace from a soul seed."""
    output_dir = Path(workspace)

    try:
        written = init_workspace(seed, output_dir)
        click.echo(f"Soul awakened! {len(written)} files generated:")
        for path in sorted(written):
            click.echo(f"  {path}")
        click.echo(f"\nWorkspace ready at: {output_dir.resolve()}")
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc))
    except ValueError as exc:
        raise click.ClickException(str(exc))


@main.command("list")
def list_seeds() -> None:
    """List all available built-in seeds."""
    seeds = list_available_seeds()

    if not seeds:
        click.echo("No seeds found.")
        return

    click.echo(f"Available seeds ({len(seeds)}):\n")
    for info in seeds:
        click.echo(f"  {info['name']:20s} {info['display_name']}")

    click.echo(f"\nUse: osp init --seed <name>")


@main.command()
@click.option("--seed", required=True, help="Seed name or path to YAML file.")
@click.option("--file", "filename", default=None, help="Specific file to preview (default: SOUL.md).")
def preview(seed: str, filename: str | None) -> None:
    """Preview the generated output for a seed."""
    try:
        content = preview_file(seed, filename)
        click.echo(content)
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc))
    except ValueError as exc:
        raise click.ClickException(str(exc))


@main.command()
@click.argument("path", type=click.Path(exists=True))
def validate(path: str) -> None:
    """Validate a YAML seed file against the OSP schema."""
    result = validate_file(path)

    if result.is_valid:
        click.echo(f"Valid: {result.path}")
    else:
        click.echo(f"Invalid: {result.path}", err=True)
        for error in result.errors:
            click.echo(f"  - {error}", err=True)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
