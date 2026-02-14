"""Tests for the OSP CLI commands.

Uses Click's CliRunner for isolated command testing.
"""

import pytest
from pathlib import Path

from click.testing import CliRunner

from osp.cli import main


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


class TestVersion:
    def test_shows_version(self, runner: CliRunner) -> None:
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "0.2.0" in result.output


class TestInit:
    def test_generates_workspace(self, runner: CliRunner, tmp_path: Path) -> None:
        workspace = tmp_path / "ws"
        result = runner.invoke(main, ["init", "--seed", "tabula_rasa", "--workspace", str(workspace)])
        assert result.exit_code == 0
        assert "Soul awakened!" in result.output
        assert "8 files generated" in result.output

    def test_creates_all_expected_files(self, runner: CliRunner, tmp_path: Path) -> None:
        workspace = tmp_path / "ws"
        runner.invoke(main, ["init", "--seed", "tabula_rasa", "--workspace", str(workspace)])

        expected_files = {"SOUL.md", "IDENTITY.md", "AGENTS.md", "MEMORY.md",
                          "HEARTBEAT.md", "BOOTSTRAP.md", "BOOT.md", "USER.md"}
        actual_files = {f.name for f in workspace.iterdir()}
        assert expected_files == actual_files

    def test_invalid_seed_shows_error(self, runner: CliRunner, tmp_path: Path) -> None:
        result = runner.invoke(main, ["init", "--seed", "nonexistent", "--workspace", str(tmp_path / "ws")])
        assert result.exit_code != 0
        assert "not found" in result.output

    def test_all_seeds_generate_successfully(self, runner: CliRunner, tmp_path: Path) -> None:
        for seed_name in ["tabula_rasa", "glitch", "sentinel", "10x_engineer"]:
            workspace = tmp_path / seed_name
            result = runner.invoke(main, ["init", "--seed", seed_name, "--workspace", str(workspace)])
            assert result.exit_code == 0, f"Failed for {seed_name}: {result.output}"


class TestList:
    def test_lists_seeds(self, runner: CliRunner) -> None:
        result = runner.invoke(main, ["list"])
        assert result.exit_code == 0
        assert "tabula_rasa" in result.output
        assert "glitch" in result.output
        assert "sentinel" in result.output
        assert "10x_engineer" in result.output

    def test_shows_display_names(self, runner: CliRunner) -> None:
        result = runner.invoke(main, ["list"])
        assert "The Observer" in result.output
        assert "The Glitch" in result.output


class TestPreview:
    def test_preview_default(self, runner: CliRunner) -> None:
        result = runner.invoke(main, ["preview", "--seed", "tabula_rasa"])
        assert result.exit_code == 0
        assert "Core Drives" in result.output

    def test_preview_specific_file(self, runner: CliRunner) -> None:
        result = runner.invoke(main, ["preview", "--seed", "glitch", "--file", "IDENTITY.md"])
        assert result.exit_code == 0
        assert "The Glitch" in result.output

    def test_preview_invalid_file(self, runner: CliRunner) -> None:
        result = runner.invoke(main, ["preview", "--seed", "tabula_rasa", "--file", "INVALID.md"])
        assert result.exit_code != 0

    def test_preview_invalid_seed(self, runner: CliRunner) -> None:
        result = runner.invoke(main, ["preview", "--seed", "nonexistent"])
        assert result.exit_code != 0


class TestValidate:
    def test_valid_seed(self, runner: CliRunner) -> None:
        seed_path = str(Path(__file__).parent.parent / "seeds" / "tabula_rasa.yaml")
        result = runner.invoke(main, ["validate", seed_path])
        assert result.exit_code == 0
        assert "Valid" in result.output

    def test_invalid_seed_file(self, runner: CliRunner, tmp_path: Path) -> None:
        bad_seed = tmp_path / "bad.yaml"
        bad_seed.write_text("nucleus:\n  drives: {}")
        result = runner.invoke(main, ["validate", str(bad_seed)])
        assert result.exit_code != 0

    def test_all_built_in_seeds_valid(self, runner: CliRunner) -> None:
        seeds_dir = Path(__file__).parent.parent / "seeds"
        for seed_file in seeds_dir.glob("*.yaml"):
            result = runner.invoke(main, ["validate", str(seed_file)])
            assert result.exit_code == 0, f"Validation failed for {seed_file.name}: {result.output}"
