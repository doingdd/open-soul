"""Generator - the orchestrator that transforms seeds into living workspaces.

Pipeline: resolve_seed_path -> load -> validate -> generate -> write
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import yaml

from osp.models import Seed
from osp.templates import TEMPLATE_REGISTRY
from osp.validator import load_seed_data, validate_file


# Built-in seeds directory (relative to project root)
SEEDS_DIR = Path(__file__).parent.parent / "seeds"


def resolve_seed_path(seed_name: str, seeds_dir: Optional[Path] = None) -> Path:
    """Resolve a seed name or path to an actual file path.

    Accepts:
      - A bare name like "tabula_rasa" (looks up in seeds_dir)
      - A full/relative file path like "seeds/custom.yaml"

    Raises:
        FileNotFoundError: If the seed cannot be found.
    """
    seeds_dir = seeds_dir or SEEDS_DIR

    # If it's already a path to an existing file, use it directly
    candidate = Path(seed_name)
    if candidate.exists() and candidate.is_file():
        return candidate

    # Try as a name in the seeds directory
    for ext in (".yaml", ".yml"):
        path = seeds_dir / f"{seed_name}{ext}"
        if path.exists():
            return path

    raise FileNotFoundError(
        f"Seed '{seed_name}' not found. "
        f"Searched in: {seeds_dir}/ and as direct path."
    )


def list_available_seeds(seeds_dir: Optional[Path] = None) -> list[dict[str, str]]:
    """List all available seed files with basic info.

    Returns a list of dicts with 'name', 'path', and 'display_name'.
    """
    seeds_dir = seeds_dir or SEEDS_DIR
    results: list[dict[str, str]] = []

    if not seeds_dir.exists():
        return results

    for path in sorted(seeds_dir.glob("*.yaml")):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            display_name = data.get("meta", {}).get("name", path.stem)
        except Exception:
            display_name = path.stem

        results.append({
            "name": path.stem,
            "path": str(path),
            "display_name": display_name,
        })

    for path in sorted(seeds_dir.glob("*.yml")):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            display_name = data.get("meta", {}).get("name", path.stem)
        except Exception:
            display_name = path.stem

        results.append({
            "name": path.stem,
            "path": str(path),
            "display_name": display_name,
        })

    return results


def generate_workspace(seed: Seed) -> dict[str, str]:
    """Generate all workspace files from a seed.

    Returns a dict mapping filename -> content.
    No filesystem writes — pure data transformation.
    """
    workspace: dict[str, str] = {}

    for filename, render_fn in TEMPLATE_REGISTRY.items():
        workspace[filename] = render_fn(seed)

    return workspace


def write_workspace(workspace: dict[str, str], output_dir: Path) -> list[Path]:
    """Write generated workspace files to disk.

    Creates the output directory if it doesn't exist.
    Returns list of written file paths.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    for filename, content in workspace.items():
        file_path = output_dir / filename
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        written.append(file_path)

    return written


def init_workspace(
    seed_name: str,
    output_dir: Path,
    seeds_dir: Optional[Path] = None,
) -> list[Path]:
    """Full pipeline: resolve -> load -> validate -> generate -> write.

    This is the main entry point for the `osp init` command.

    Raises:
        FileNotFoundError: If seed not found.
        ValueError: If seed is invalid.
    """
    # Resolve
    seed_path = resolve_seed_path(seed_name, seeds_dir)

    # Load & validate
    raw_data = load_seed_data(seed_path)

    # Parse into model
    seed = Seed.from_dict(raw_data)

    # Generate
    workspace = generate_workspace(seed)

    # Write
    return write_workspace(workspace, output_dir)


def preview_file(
    seed_name: str,
    filename: Optional[str] = None,
    seeds_dir: Optional[Path] = None,
) -> str:
    """Preview a specific file or SOUL.md by default.

    Returns the rendered content as a string.
    """
    seed_path = resolve_seed_path(seed_name, seeds_dir)
    raw_data = load_seed_data(seed_path)
    seed = Seed.from_dict(raw_data)

    target = filename or "SOUL.md"

    if target not in TEMPLATE_REGISTRY:
        available = ", ".join(sorted(TEMPLATE_REGISTRY.keys()))
        raise ValueError(f"Unknown file '{target}'. Available: {available}")

    return TEMPLATE_REGISTRY[target](seed)
