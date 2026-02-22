"""Updater - version tracking and seed update functionality.

Provides functions to read/write workspace metadata and check for updates.
Phase 3: Update pipeline (backup, file strategies, update_workspace).
"""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

import osp

from osp.merger import MergeStrategy, merge_agents_md, merge_soul_md, merge_story_md
from osp.models import OSPMeta, Seed
from osp.generator import generate_workspace, resolve_seed_path
from osp.validator import load_seed_data


# === Data Structures ===


@dataclass(frozen=True)
class FileChange:
    """Record of a single file change during update."""

    filename: str
    action: str  # "overwritten", "preserved", "smart_merged", "section_merged", "union_merged", "skipped"
    details: str


@dataclass(frozen=True)
class UpdateResult:
    """Result of a workspace update operation."""

    success: bool
    from_version: float
    to_version: float
    changes: tuple[FileChange, ...]
    backup_path: str | None
    conflicts: tuple[str, ...]


# === File Strategy Mapping ===

FILE_STRATEGIES: dict[str, MergeStrategy] = {
    "IDENTITY.md": MergeStrategy.OVERWRITE,
    "BOOTSTRAP.md": MergeStrategy.OVERWRITE,
    "HEARTBEAT.md": MergeStrategy.OVERWRITE,
    "SOUL.md": MergeStrategy.SMART_MERGE,
    "STORY.md": MergeStrategy.SECTION_MERGE,
    "AGENTS.md": MergeStrategy.UNION_MERGE,
    "MEMORY.md": MergeStrategy.PRESERVE,
    "USER.md": MergeStrategy.PRESERVE,
    "EVOLUTION_LOG.md": MergeStrategy.PRESERVE,
    "BOOT.md": MergeStrategy.SMART_MERGE,
}


def get_meta_path(workspace: Path) -> Path:
    """Get the path to .osp/meta.json for a workspace.

    Args:
        workspace: Path to the workspace directory.

    Returns:
        Path to the meta.json file (workspace/.osp/meta.json).
    """
    return workspace / ".osp" / "meta.json"


def read_osp_meta(workspace: Path) -> Optional[OSPMeta]:
    """Read workspace metadata from .osp/meta.json.

    Args:
        workspace: Path to the workspace directory.

    Returns:
        OSPMeta if valid metadata exists, None otherwise.
    """
    meta_path = get_meta_path(workspace)

    if not meta_path.exists():
        return None

    try:
        with open(meta_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return OSPMeta.from_dict(data)
    except (json.JSONDecodeError, KeyError, TypeError, ValueError):
        return None


def get_file_strategy(filename: str) -> MergeStrategy:
    """Get the merge strategy for a specific file.

    Args:
        filename: The name of the file (e.g., "SOUL.md").

    Returns:
        The MergeStrategy to use. Defaults to PRESERVE for unknown files.
    """
    return FILE_STRATEGIES.get(filename, MergeStrategy.PRESERVE)


def create_backup(workspace: Path) -> Path:
    """Create a backup of all .md files in the workspace.

    Creates a timestamped backup directory under .osp/backups/.

    Args:
        workspace: Path to the workspace directory.

    Returns:
        Path to the created backup directory.
    """
    # Create timestamp for backup directory name
    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    backup_dir = workspace / ".osp" / "backups" / timestamp
    backup_dir.mkdir(parents=True, exist_ok=True)

    # Copy all .md files to backup
    for md_file in workspace.glob("*.md"):
        backup_file = backup_dir / md_file.name
        shutil.copy2(md_file, backup_file)

    return backup_dir


def update_file(
    workspace: Path,
    filename: str,
    upstream_content: str,
    strategy: MergeStrategy,
) -> FileChange:
    """Update a single file according to the merge strategy.

    Args:
        workspace: Path to the workspace directory.
        filename: Name of the file to update.
        upstream_content: The new content from upstream.
        strategy: The merge strategy to use.

    Returns:
        FileChange record describing what happened.
    """
    file_path = workspace / filename

    # Skip empty upstream content
    if not upstream_content or not upstream_content.strip():
        return FileChange(
            filename=filename,
            action="skipped",
            details="Empty upstream content",
        )

    # Get local content if exists
    local_content: Optional[str] = None
    if file_path.exists():
        local_content = file_path.read_text(encoding="utf-8")

    # Apply strategy
    if strategy == MergeStrategy.OVERWRITE:
        file_path.write_text(upstream_content, encoding="utf-8")
        return FileChange(
            filename=filename,
            action="overwritten",
            details="Replaced with upstream content",
        )

    elif strategy == MergeStrategy.PRESERVE:
        if local_content is None:
            # No local file, create it with upstream content
            file_path.write_text(upstream_content, encoding="utf-8")
            return FileChange(
                filename=filename,
                action="overwritten",
                details="Created with upstream (no local file)",
            )
        else:
            # Keep local content unchanged
            return FileChange(
                filename=filename,
                action="preserved",
                details="Local content preserved",
            )

    elif strategy == MergeStrategy.SMART_MERGE:
        merged = merge_soul_md(local_content, upstream_content)
        file_path.write_text(merged, encoding="utf-8")
        return FileChange(
            filename=filename,
            action="smart_merged",
            details="Smart merge (preserved local drive values)",
        )

    elif strategy == MergeStrategy.SECTION_MERGE:
        merged = merge_story_md(local_content, upstream_content)
        file_path.write_text(merged, encoding="utf-8")
        return FileChange(
            filename=filename,
            action="section_merged",
            details="Section merge (preserved 'Our Story' section)",
        )

    elif strategy == MergeStrategy.UNION_MERGE:
        merged = merge_agents_md(local_content, upstream_content)
        file_path.write_text(merged, encoding="utf-8")
        return FileChange(
            filename=filename,
            action="union_merged",
            details="Union merge (combined skills)",
        )

    else:
        # Default to preserve for unknown strategies
        return FileChange(
            filename=filename,
            action="preserved",
            details=f"Unknown strategy: {strategy}",
        )


def write_updated_meta(workspace: Path, seed: Seed, seed_file: str) -> None:
    """Write updated metadata after a successful update.

    Args:
        workspace: Path to the workspace directory.
        seed: The seed that was updated to.
        seed_file: The seed file name for future updates.
    """
    osp_dir = workspace / ".osp"
    osp_dir.mkdir(parents=True, exist_ok=True)

    meta = OSPMeta(
        seed_id=seed.meta.seed_id,
        seed_name=seed.meta.name,
        seed_file=seed_file,
        installed_version=seed.meta.version,
        installed_at=datetime.now().isoformat(timespec="seconds"),
        osp_version=osp.__version__,
    )

    meta_path = osp_dir / "meta.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta.to_dict(), f, indent=2)


def update_workspace(
    workspace: Path,
    seed_name: Optional[str] = None,
    dry_run: bool = False,
    force: bool = False,
) -> UpdateResult:
    """Update a workspace with the latest seed version.

    Pipeline:
    1. Read local meta
    2. Load upstream seed
    3. Compare versions
    4. Create backup (if not dry_run)
    5. Apply file strategies
    6. Update meta
    7. Return result

    Args:
        workspace: Path to the workspace directory.
        seed_name: Optional seed name to update to. If None, uses meta's seed_id.
        dry_run: If True, simulate update without modifying files.
        force: If True, allow update even without existing meta.

    Returns:
        UpdateResult with success status, changes, and any conflicts.
    """
    conflicts: list[str] = []
    changes: list[FileChange] = []
    backup_path: Optional[str] = None

    # Step 1: Read local meta
    local_meta = read_osp_meta(workspace)

    if local_meta is None and not force:
        return UpdateResult(
            success=False,
            from_version=0.0,
            to_version=0.0,
            changes=(),
            backup_path=None,
            conflicts=("No .osp/meta.json found. Use --force to initialize.",),
        )

    # Determine seed to use (prefer seed_file over seed_id for lookup)
    target_seed_name = seed_name
    if target_seed_name is None and local_meta is not None:
        # Use seed_file if available, otherwise fall back to seed_id
        target_seed_name = local_meta.seed_file if local_meta.seed_file else local_meta.seed_id

    if target_seed_name is None:
        return UpdateResult(
            success=False,
            from_version=0.0,
            to_version=0.0,
            changes=(),
            backup_path=None,
            conflicts=("No seed name specified and no meta found.",),
        )

    # Step 2: Load upstream seed
    try:
        seed_path = resolve_seed_path(target_seed_name)
        raw_data = load_seed_data(seed_path)
        upstream_seed = Seed.from_dict(raw_data)
    except FileNotFoundError:
        return UpdateResult(
            success=False,
            from_version=local_meta.installed_version if local_meta else 0.0,
            to_version=0.0,
            changes=(),
            backup_path=None,
            conflicts=(f"Seed '{target_seed_name}' not found.",),
        )
    except Exception as e:
        return UpdateResult(
            success=False,
            from_version=local_meta.installed_version if local_meta else 0.0,
            to_version=0.0,
            changes=(),
            backup_path=None,
            conflicts=(f"Failed to load seed: {e}",),
        )

    from_version = local_meta.installed_version if local_meta else 0.0
    to_version = upstream_seed.meta.version

    # Step 3: Generate upstream workspace content
    upstream_workspace = generate_workspace(upstream_seed)

    # Step 4: Create backup (if not dry_run)
    if not dry_run and workspace.exists():
        # Check if there are any .md files to backup
        if list(workspace.glob("*.md")):
            backup_dir = create_backup(workspace)
            backup_path = str(backup_dir)

    # Step 5: Apply file strategies
    for filename, upstream_content in upstream_workspace.items():
        strategy = get_file_strategy(filename)

        if dry_run:
            # In dry run, just record what would happen
            if strategy == MergeStrategy.OVERWRITE:
                action = "overwritten"
                details = "Would replace with upstream content"
            elif strategy == MergeStrategy.PRESERVE:
                action = "preserved"
                details = "Would preserve local content"
            elif strategy == MergeStrategy.SMART_MERGE:
                action = "smart_merged"
                details = "Would smart merge"
            elif strategy == MergeStrategy.SECTION_MERGE:
                action = "section_merged"
                details = "Would section merge"
            elif strategy == MergeStrategy.UNION_MERGE:
                action = "union_merged"
                details = "Would union merge"
            else:
                action = "preserved"
                details = f"Unknown strategy: {strategy}"

            changes.append(FileChange(filename=filename, action=action, details=details))
        else:
            # Actually update the file
            change = update_file(workspace, filename, upstream_content, strategy)
            changes.append(change)

    # Step 6: Update meta (if not dry_run)
    if not dry_run:
        write_updated_meta(workspace, upstream_seed, target_seed_name)

    # Step 7: Return result
    return UpdateResult(
        success=True,
        from_version=from_version,
        to_version=to_version,
        changes=tuple(changes),
        backup_path=backup_path,
        conflicts=tuple(conflicts),
    )
