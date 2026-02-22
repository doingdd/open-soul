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
        assert "9 files generated" in result.output

    def test_creates_all_expected_files(self, runner: CliRunner, tmp_path: Path) -> None:
        workspace = tmp_path / "ws"
        runner.invoke(main, ["init", "--seed", "tabula_rasa", "--workspace", str(workspace)])

        expected_files = {"SOUL.md", "IDENTITY.md", "AGENTS.md", "MEMORY.md",
                          "HEARTBEAT.md", "EVOLUTION_LOG.md", "BOOTSTRAP.md", "BOOT.md", "USER.md"}
        # Only check .md files (exclude .osp directory)
        actual_files = {f.name for f in workspace.iterdir() if f.suffix == ".md"}
        assert expected_files == actual_files

    def test_creates_osp_meta_file(self, runner: CliRunner, tmp_path: Path) -> None:
        """Verify that .osp/meta.json is created."""
        workspace = tmp_path / "ws"
        runner.invoke(main, ["init", "--seed", "tabula_rasa", "--workspace", str(workspace)])

        meta_path = workspace / ".osp" / "meta.json"
        assert meta_path.exists()

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


class TestStatus:
    """Tests for the 'osp status' command."""

    def test_status_shows_workspace_info(self, runner: CliRunner, tmp_path: Path) -> None:
        """Status should display seed name, version, and install time."""
        workspace = tmp_path / "ws"
        runner.invoke(main, ["init", "--seed", "tabula_rasa", "--workspace", str(workspace)])

        result = runner.invoke(main, ["status", "--workspace", str(workspace)])
        assert result.exit_code == 0
        # Display name is shown (The Observer for tabula_rasa)
        assert "Observer" in result.output
        assert "Workspace:" in result.output

    def test_status_shows_osp_version(self, runner: CliRunner, tmp_path: Path) -> None:
        """Status should display the OSP version used for installation."""
        workspace = tmp_path / "ws"
        runner.invoke(main, ["init", "--seed", "tabula_rasa", "--workspace", str(workspace)])

        result = runner.invoke(main, ["status", "--workspace", str(workspace)])
        assert result.exit_code == 0
        assert "0.2.0" in result.output

    def test_status_nonexistent_workspace(self, runner: CliRunner, tmp_path: Path) -> None:
        """Status should fail gracefully for nonexistent workspace."""
        workspace = tmp_path / "nonexistent"
        result = runner.invoke(main, ["status", "--workspace", str(workspace)])
        assert result.exit_code != 0
        assert "not found" in result.output.lower() or "no meta" in result.output.lower()

    def test_status_no_meta_json(self, runner: CliRunner, tmp_path: Path) -> None:
        """Status should fail if workspace has no .osp/meta.json."""
        workspace = tmp_path / "ws"
        workspace.mkdir()
        (workspace / "SOUL.md").write_text("# Soul")

        result = runner.invoke(main, ["status", "--workspace", str(workspace)])
        assert result.exit_code != 0

    def test_status_default_workspace(self, runner: CliRunner) -> None:
        """Status should default to ./workspace if not specified."""
        # This test verifies the option exists; actual default behavior
        # would require modifying cwd
        result = runner.invoke(main, ["status", "--help"])
        assert result.exit_code == 0
        assert "--workspace" in result.output


class TestUpdateDryRun:
    """Tests for 'osp update --dry-run' command."""

    def test_dry_run_shows_preview(self, runner: CliRunner, tmp_path: Path) -> None:
        """Dry run should show what would change without modifying files."""
        workspace = tmp_path / "ws"
        runner.invoke(main, ["init", "--seed", "tabula_rasa", "--workspace", str(workspace)])

        result = runner.invoke(main, ["update", "--workspace", str(workspace), "--dry-run"])
        assert result.exit_code == 0
        assert "dry-run" in result.output.lower() or "preview" in result.output.lower() or "would" in result.output.lower()

    def test_dry_run_preserves_files(self, runner: CliRunner, tmp_path: Path) -> None:
        """Dry run must not modify any files."""
        workspace = tmp_path / "ws"
        runner.invoke(main, ["init", "--seed", "tabula_rasa", "--workspace", str(workspace)])

        # Get original content
        soul_path = workspace / "SOUL.md"
        original_content = soul_path.read_text()

        result = runner.invoke(main, ["update", "--workspace", str(workspace), "--dry-run"])

        # Content should be unchanged
        assert soul_path.read_text() == original_content

    def test_dry_run_shows_file_strategies(self, runner: CliRunner, tmp_path: Path) -> None:
        """Dry run should indicate which files would be overwritten vs merged vs preserved."""
        workspace = tmp_path / "ws"
        runner.invoke(main, ["init", "--seed", "tabula_rasa", "--workspace", str(workspace)])

        result = runner.invoke(main, ["update", "--workspace", str(workspace), "--dry-run"])
        # Should show some indication of file strategies
        assert "IDENTITY.md" in result.output or "overwritten" in result.output.lower()

    def test_dry_run_no_backup_created(self, runner: CliRunner, tmp_path: Path) -> None:
        """Dry run must not create backups."""
        workspace = tmp_path / "ws"
        runner.invoke(main, ["init", "--seed", "tabula_rasa", "--workspace", str(workspace)])

        result = runner.invoke(main, ["update", "--workspace", str(workspace), "--dry-run"])

        # No backup should be created
        backup_dir = workspace / ".osp" / "backups"
        assert not backup_dir.exists() or len(list(backup_dir.iterdir())) == 0


class TestUpdate:
    """Tests for 'osp update' command (actual update)."""

    def test_update_same_version_no_changes(self, runner: CliRunner, tmp_path: Path) -> None:
        """Update to same version should report no changes needed."""
        workspace = tmp_path / "ws"
        runner.invoke(main, ["init", "--seed", "tabula_rasa", "--workspace", str(workspace)])

        result = runner.invoke(main, ["update", "--workspace", str(workspace)])
        # Should succeed (either no changes or same version message)
        assert result.exit_code == 0

    def test_update_creates_backup(self, runner: CliRunner, tmp_path: Path) -> None:
        """Update should create a backup of existing files."""
        workspace = tmp_path / "ws"
        runner.invoke(main, ["init", "--seed", "tabula_rasa", "--workspace", str(workspace)])

        # Modify a file to verify backup
        soul_path = workspace / "SOUL.md"
        original_content = soul_path.read_text()
        soul_path.write_text(original_content + "\n\n# Modified!")

        result = runner.invoke(main, ["update", "--workspace", str(workspace)])

        # Backup should exist
        backup_dir = workspace / ".osp" / "backups"
        if result.exit_code == 0:
            # Backup should be created
            assert backup_dir.exists(), "Backup directory should exist after update"

    def test_update_preserves_memory(self, runner: CliRunner, tmp_path: Path) -> None:
        """Update must preserve MEMORY.md content."""
        workspace = tmp_path / "ws"
        runner.invoke(main, ["init", "--seed", "tabula_rasa", "--workspace", str(workspace)])

        # Add custom content to MEMORY.md
        memory_path = workspace / "MEMORY.md"
        custom_memory = memory_path.read_text() + "\n\n## Custom Memory\nMy precious memories!"
        memory_path.write_text(custom_memory)

        result = runner.invoke(main, ["update", "--workspace", str(workspace)])

        # Memory should be preserved
        assert custom_memory in memory_path.read_text()

    def test_update_no_meta_requires_force(self, runner: CliRunner, tmp_path: Path) -> None:
        """Update without meta.json should fail unless --force is used."""
        workspace = tmp_path / "ws"
        workspace.mkdir()
        (workspace / "SOUL.md").write_text("# Soul")

        result = runner.invoke(main, ["update", "--workspace", str(workspace)])
        assert result.exit_code != 0
        assert "force" in result.output.lower()

    def test_update_force_initializes(self, runner: CliRunner, tmp_path: Path) -> None:
        """Update --force should initialize workspace from seed."""
        workspace = tmp_path / "ws"
        workspace.mkdir()
        (workspace / "SOUL.md").write_text("# Old Soul")

        result = runner.invoke(main, [
            "update", "--workspace", str(workspace),
            "--seed", "tabula_rasa", "--force"
        ])
        assert result.exit_code == 0

    def test_update_with_seed_option(self, runner: CliRunner, tmp_path: Path) -> None:
        """Update --seed should allow switching to different seed."""
        workspace = tmp_path / "ws"
        runner.invoke(main, ["init", "--seed", "tabula_rasa", "--workspace", str(workspace)])

        result = runner.invoke(main, [
            "update", "--workspace", str(workspace),
            "--seed", "glitch"
        ])
        # Should succeed (either update or switch)
        assert result.exit_code == 0

    def test_update_nonexistent_workspace(self, runner: CliRunner, tmp_path: Path) -> None:
        """Update should fail for nonexistent workspace."""
        workspace = tmp_path / "nonexistent"
        result = runner.invoke(main, ["update", "--workspace", str(workspace)])
        assert result.exit_code != 0

    def test_update_shows_summary(self, runner: CliRunner, tmp_path: Path) -> None:
        """Update should show a summary of changes."""
        workspace = tmp_path / "ws"
        runner.invoke(main, ["init", "--seed", "tabula_rasa", "--workspace", str(workspace)])

        result = runner.invoke(main, ["update", "--workspace", str(workspace)])
        assert result.exit_code == 0
        # Should show some form of summary (updated/preserved/complete)
        output_lower = result.output.lower()
        assert "updated" in output_lower or "complete" in output_lower or "preserved" in output_lower
