"""Seed validation engine - enforces the soul's structural integrity.

Extracted from the original test_seeds.py into a reusable module.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Union

import yaml

# The law every soul must obey
SOUL_SCHEMA = {
    "required_roots": ["meta", "nucleus", "persona", "pulse"],
    "meta": ["seed_id", "name", "version"],
    "nucleus": ["drives", "prime_directives"],
    "persona": ["current_mission", "unlocked_skills", "memory_summary"],
    "pulse": ["tone", "formatting_preference"],
}


@dataclass(frozen=True)
class ValidationResult:
    """Immutable validation outcome."""

    path: str
    errors: tuple[str, ...] = field(default_factory=tuple)

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0


def validate_structure(data: dict, filename: str = "<unknown>") -> list[str]:
    """Validate a seed dictionary against the OSP schema.

    Returns a list of error messages (empty if valid).
    """
    errors: list[str] = []

    if not isinstance(data, dict):
        return [f"Expected a YAML mapping, got {type(data).__name__}"]

    # Check root sections
    for root in SOUL_SCHEMA["required_roots"]:
        if root not in data:
            errors.append(f"Missing root section: '{root}'")

    # Check meta fields
    if "meta" in data and isinstance(data["meta"], dict):
        for fld in SOUL_SCHEMA["meta"]:
            if fld not in data["meta"]:
                errors.append(f"Missing field in meta: '{fld}'")

    # Check Nucleus (Layer 1)
    if "nucleus" in data and isinstance(data["nucleus"], dict):
        for fld in SOUL_SCHEMA["nucleus"]:
            if fld not in data["nucleus"]:
                errors.append(f"Missing field in nucleus: '{fld}'")

        drives = data["nucleus"].get("drives")
        if isinstance(drives, dict):
            for drive_name, value in drives.items():
                try:
                    fval = float(value)
                    if not (0.0 <= fval <= 1.0):
                        errors.append(
                            f"Drive '{drive_name}' value {value} out of range [0.0, 1.0]"
                        )
                except (ValueError, TypeError):
                    errors.append(
                        f"Drive '{drive_name}' value '{value}' is not a number"
                    )

    # Check Persona (Layer 2)
    if "persona" in data and isinstance(data["persona"], dict):
        for fld in SOUL_SCHEMA["persona"]:
            if fld not in data["persona"]:
                errors.append(f"Missing field in persona: '{fld}'")

    # Check Pulse (Layer 3)
    if "pulse" in data and isinstance(data["pulse"], dict):
        for fld in SOUL_SCHEMA["pulse"]:
            if fld not in data["pulse"]:
                errors.append(f"Missing field in pulse: '{fld}'")

    return errors


def validate_file(path: Union[str, Path]) -> ValidationResult:
    """Validate a single YAML seed file.

    Returns a ValidationResult with any errors found.
    """
    path = Path(path)
    str_path = str(path)

    if not path.exists():
        return ValidationResult(path=str_path, errors=(f"File not found: {str_path}",))

    if not path.suffix in (".yaml", ".yml"):
        return ValidationResult(
            path=str_path, errors=(f"Not a YAML file: {str_path}",)
        )

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as exc:
        return ValidationResult(
            path=str_path, errors=(f"Invalid YAML syntax: {exc}",)
        )

    if not data:
        return ValidationResult(path=str_path, errors=("File is empty",))

    errs = validate_structure(data, str_path)
    return ValidationResult(path=str_path, errors=tuple(errs))


def load_seed_data(path: Union[str, Path]) -> dict:
    """Load and return raw YAML data from a seed file.

    Raises:
        FileNotFoundError: If the file doesn't exist.
        yaml.YAMLError: If YAML parsing fails.
        ValueError: If the file is empty or invalid.
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Seed file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not data:
        raise ValueError(f"Seed file is empty: {path}")

    errors = validate_structure(data, str(path))
    if errors:
        raise ValueError(f"Seed validation failed for {path}:\n" + "\n".join(f"  - {e}" for e in errors))

    return data
