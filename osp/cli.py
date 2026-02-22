"""OSP CLI - Transform seeds into living AI workspaces.

Usage:
    osp init --seed tabula_rasa
    osp list
    osp preview --seed glitch
    osp validate seeds/my_seed.yaml
    osp status --workspace ./workspace
    osp update --workspace ./workspace [--dry-run] [--force]
"""

from __future__ import annotations

from pathlib import Path

import click

from osp import __version__
from osp.generator import (
    init_workspace,
    list_available_seeds,
    preview_file,
)
from osp.updater import read_osp_meta, update_workspace
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
    except (FileNotFoundError, ValueError) as exc:
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
    except (FileNotFoundError, ValueError) as exc:
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


@main.command()
@click.option(
    "--workspace",
    default="./workspace",
    type=click.Path(),
    help="Path to the workspace directory.",
)
def status(workspace: str) -> None:
    """Display workspace status including seed info and version."""
    workspace_path = Path(workspace)

    if not workspace_path.exists():
        raise click.ClickException(f"Workspace not found: {workspace}")

    meta = read_osp_meta(workspace_path)

    if meta is None:
        raise click.ClickException(f"No .osp/meta.json found in: {workspace}")

    click.echo(f"Workspace: {workspace_path.resolve()}")
    click.echo(f"Seed: {meta.seed_name} (v{meta.installed_version})")
    click.echo(f"Installed: {meta.installed_at}")
    click.echo(f"OSP Version: {meta.osp_version}")


@main.command()
@click.option(
    "--workspace",
    default="./workspace",
    type=click.Path(),
    help="Path to the workspace directory.",
)
@click.option("--seed", default=None, help="Seed name to update to (optional).")
@click.option("--dry-run", is_flag=True, help="Preview changes without modifying files.")
@click.option("--force", is_flag=True, help="Force update even without existing meta.")
def update(workspace: str, seed: str | None, dry_run: bool, force: bool) -> None:
    """Update workspace with the latest seed version."""
    workspace_path = Path(workspace)

    if not workspace_path.exists():
        raise click.ClickException(f"Workspace not found: {workspace}")

    if dry_run:
        click.echo("Checking for updates...")

    result = update_workspace(
        workspace=workspace_path,
        seed_name=seed,
        dry_run=dry_run,
        force=force,
    )

    if not result.success:
        for conflict in result.conflicts:
            click.echo(f"Error: {conflict}", err=True)
        raise SystemExit(1)

    # Display version info
    if result.from_version != result.to_version:
        click.echo(f"Updating from v{result.from_version} to v{result.to_version}...")
    else:
        click.echo(f"Current: v{result.from_version} (latest)")

    # Display changes
    if dry_run:
        click.echo("\nChanges (dry-run):")
        for change in result.changes:
            click.echo(f"  {change.filename}: {change.details}")
        click.echo("\nRun without --dry-run to apply changes.")
    else:
        # Categorize changes
        overwritten = [c for c in result.changes if c.action == "overwritten"]
        merged = [c for c in result.changes if "merged" in c.action]
        preserved = [c for c in result.changes if c.action == "preserved"]
        skipped = [c for c in result.changes if c.action == "skipped"]

        if overwritten:
            click.echo("\nUpdated:")
            for change in overwritten:
                click.echo(f"  {change.filename}: overwritten")

        if merged:
            click.echo("\nMerged:")
            for change in merged:
                click.echo(f"  {change.filename}: {change.action.replace('_', ' ')}")

        if preserved:
            click.echo("\nPreserved:")
            for change in preserved:
                click.echo(f"  {change.filename}")

        if result.backup_path:
            click.echo(f"\nBackup created: {result.backup_path}")

        click.echo("\nUpdate complete!")


if __name__ == "__main__":
    main()
