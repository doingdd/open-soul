"""Seed validation tests - verifies all YAML seeds against the OSP schema.

Uses the osp.validator module for validation logic.
Can also run standalone: python tests/test_seeds.py
"""

import glob
import sys
from pathlib import Path

import pytest
import yaml

from osp.validator import validate_file, validate_structure
from osp.models import Seed

SEEDS_DIR = Path(__file__).parent.parent / "seeds"


# === Pytest-compatible tests ===

class TestSeedValidation:
    """Validate all seed files using the validator module."""

    @pytest.fixture(params=sorted(SEEDS_DIR.glob("*.yaml")), ids=lambda p: p.stem)
    def seed_path(self, request: pytest.FixtureRequest) -> Path:
        return request.param

    def test_seed_is_valid(self, seed_path: Path) -> None:
        result = validate_file(seed_path)
        assert result.is_valid, f"Errors in {seed_path.name}: {result.errors}"

    def test_seed_parses_to_model(self, seed_path: Path) -> None:
        with open(seed_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        seed = Seed.from_dict(data)
        assert seed.meta.name
        assert isinstance(seed.nucleus.drives, dict)
        assert isinstance(seed.nucleus.prime_directives, list)


class TestValidationEdgeCases:
    """Test validation with intentionally broken data."""

    def test_empty_data(self) -> None:
        errors = validate_structure({}, "test")
        assert len(errors) == 4  # missing all 4 root sections

    def test_missing_nucleus(self) -> None:
        data = {"meta": {}, "persona": {}, "pulse": {}}
        errors = validate_structure(data)
        assert any("nucleus" in e for e in errors)

    def test_drive_out_of_range(self) -> None:
        data = {
            "meta": {"seed_id": "x", "name": "x", "version": 1.0},
            "nucleus": {"drives": {"test": 1.5}, "prime_directives": []},
            "persona": {"current_mission": None, "unlocked_skills": [], "memory_summary": ""},
            "pulse": {"tone": [], "formatting_preference": "text"},
        }
        errors = validate_structure(data)
        assert any("out of range" in e for e in errors)

    def test_non_numeric_drive(self) -> None:
        data = {
            "meta": {"seed_id": "x", "name": "x", "version": 1.0},
            "nucleus": {"drives": {"test": "not_a_number"}, "prime_directives": []},
            "persona": {"current_mission": None, "unlocked_skills": [], "memory_summary": ""},
            "pulse": {"tone": [], "formatting_preference": "text"},
        }
        errors = validate_structure(data)
        assert any("not a number" in e for e in errors)


# === Standalone script mode (backward compatibility) ===

def main() -> None:
    seed_files = glob.glob("seeds/**/*.yaml", recursive=True)
    if not seed_files:
        print("No seeds found in seeds/")
        return

    failed_count = 0
    print(f"Found {len(seed_files)} seeds. Validating...")
    print("-" * 40)

    for f in seed_files:
        result = validate_file(f)
        if result.is_valid:
            print(f"  {f}: PASSED")
        else:
            print(f"  {f}: FAILED")
            for e in result.errors:
                print(f"   - {e}")
            failed_count += 1

    print("-" * 40)
    if failed_count > 0:
        print(f"Validation failed! {failed_count} seeds have errors.")
        sys.exit(1)
    else:
        print("All seeds look good!")
        sys.exit(0)


if __name__ == "__main__":
    main()
