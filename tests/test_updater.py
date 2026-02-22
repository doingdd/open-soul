"""Tests for version tracking and seed update functionality.

Phase 1: OSPMeta model and basic reader functions.
Phase 3: Update pipeline (backup, file strategies, update_workspace).
"""

import json
from pathlib import Path

import pytest

from osp.models import OSPMeta, Seed


# === Fixtures ===

@pytest.fixture
def sample_seed_data() -> dict:
    return {
        "meta": {
            "seed_id": "test_001",
            "name": "Test Soul",
            "version": 1.0,
            "created_at": "2024-01-01",
        },
        "nucleus": {
            "drives": {"curiosity": 0.8, "empathy": 0.5},
            "prime_directives": ["Be honest.", "Stay curious."],
        },
        "persona": {
            "current_mission": "Explore the unknown.",
            "mission_lock": False,
            "memory_summary": "I just woke up.",
            "unlocked_skills": ["fs.read", "shell.exec"],
        },
        "pulse": {
            "tone": ["calm", "thoughtful"],
            "formatting_preference": "markdown",
            "quirks": ["Often pauses mid-sentence..."],
        },
    }


@pytest.fixture
def sample_seed(sample_seed_data: dict) -> Seed:
    return Seed.from_dict(sample_seed_data)


@pytest.fixture
def sample_osp_meta_data() -> dict:
    return {
        "seed_id": "test_001",
        "seed_name": "Test Soul",
        "installed_version": 1.0,
        "installed_at": "2024-01-15T10:30:00",
        "osp_version": "0.2.0",
    }


@pytest.fixture
def tmp_workspace(tmp_path: Path) -> Path:
    return tmp_path / "workspace"


# === OSPMeta Model Tests ===

class TestOSPMetaModel:
    """Test the OSPMeta frozen dataclass."""

    def test_create_osp_meta(self, sample_osp_meta_data: dict) -> None:
        """OSPMeta can be created with all required fields."""
        meta = OSPMeta(
            seed_id=sample_osp_meta_data["seed_id"],
            seed_name=sample_osp_meta_data["seed_name"],
            seed_file="test_seed",
            installed_version=sample_osp_meta_data["installed_version"],
            installed_at=sample_osp_meta_data["installed_at"],
            osp_version=sample_osp_meta_data["osp_version"],
        )
        assert meta.seed_id == "test_001"
        assert meta.seed_name == "Test Soul"
        assert meta.seed_file == "test_seed"
        assert meta.installed_version == 1.0
        assert meta.installed_at == "2024-01-15T10:30:00"
        assert meta.osp_version == "0.2.0"

    def test_osp_meta_is_frozen(self, sample_osp_meta_data: dict) -> None:
        """OSPMeta is immutable - cannot modify after creation."""
        meta = OSPMeta(
            seed_id=sample_osp_meta_data["seed_id"],
            seed_name=sample_osp_meta_data["seed_name"],
            seed_file="test_seed",
            installed_version=sample_osp_meta_data["installed_version"],
            installed_at=sample_osp_meta_data["installed_at"],
            osp_version=sample_osp_meta_data["osp_version"],
        )
        with pytest.raises(AttributeError):
            meta.seed_id = "modified"  # type: ignore[misc]

    def test_osp_meta_from_dict(self, sample_osp_meta_data: dict) -> None:
        """OSPMeta can be created from a dictionary."""
        meta = OSPMeta.from_dict(sample_osp_meta_data)
        assert meta.seed_id == "test_001"
        assert meta.seed_name == "Test Soul"
        assert meta.installed_version == 1.0
        assert meta.installed_at == "2024-01-15T10:30:00"
        assert meta.osp_version == "0.2.0"

    def test_osp_meta_to_dict(self, sample_osp_meta_data: dict) -> None:
        """OSPMeta can be serialized to a dictionary."""
        meta = OSPMeta.from_dict(sample_osp_meta_data)
        result = meta.to_dict()
        # Check that all expected keys are present
        assert "seed_id" in result
        assert "seed_name" in result
        assert "seed_file" in result
        assert "installed_version" in result
        assert "installed_at" in result
        assert "osp_version" in result

    def test_osp_meta_from_dict_with_version_as_string(self) -> None:
        """OSPMeta.from_dict should handle version as string."""
        data = {
            "seed_id": "test_002",
            "seed_name": "Version String Test",
            "seed_file": "version_test",
            "installed_version": "2.5",  # String instead of float
            "installed_at": "2024-02-01",
            "osp_version": "0.3.0",
        }
        meta = OSPMeta.from_dict(data)
        assert meta.installed_version == 2.5
        assert isinstance(meta.installed_version, float)

    def test_osp_meta_to_dict_is_json_serializable(self, sample_osp_meta_data: dict) -> None:
        """OSPMeta.to_dict produces JSON-serializable output."""
        meta = OSPMeta.from_dict(sample_osp_meta_data)
        result = meta.to_dict()
        # Should not raise
        json_str = json.dumps(result)
        assert json.loads(json_str) == result


# === Updater Basic Functions Tests ===

class TestGetMetaPath:
    """Test the get_meta_path function."""

    def test_get_meta_path_returns_correct_location(self, tmp_workspace: Path) -> None:
        """get_meta_path returns .osp/meta.json path."""
        from osp.updater import get_meta_path

        result = get_meta_path(tmp_workspace)
        expected = tmp_workspace / ".osp" / "meta.json"
        assert result == expected

    def test_get_meta_path_works_with_nonexistent_workspace(self, tmp_path: Path) -> None:
        """get_meta_path works even if workspace doesn't exist."""
        from osp.updater import get_meta_path

        nonexistent = tmp_path / "does_not_exist"
        result = get_meta_path(nonexistent)
        assert result.parent.parent == nonexistent


class TestReadOSPMeta:
    """Test the read_osp_meta function."""

    def test_read_osp_meta_returns_none_when_no_meta(self, tmp_workspace: Path) -> None:
        """read_osp_meta returns None if .osp/meta.json doesn't exist."""
        from osp.updater import read_osp_meta

        result = read_osp_meta(tmp_workspace)
        assert result is None

    def test_read_osp_meta_returns_meta_when_exists(self, tmp_workspace: Path, sample_osp_meta_data: dict) -> None:
        """read_osp_meta returns OSPMeta when .osp/meta.json exists."""
        from osp.updater import read_osp_meta

        # Create .osp/meta.json
        osp_dir = tmp_workspace / ".osp"
        osp_dir.mkdir(parents=True)
        meta_path = osp_dir / "meta.json"
        meta_path.write_text(json.dumps(sample_osp_meta_data), encoding="utf-8")

        result = read_osp_meta(tmp_workspace)
        assert result is not None
        assert result.seed_id == "test_001"
        assert result.seed_name == "Test Soul"

    def test_read_osp_meta_handles_invalid_json(self, tmp_workspace: Path) -> None:
        """read_osp_meta returns None if meta.json is invalid JSON."""
        from osp.updater import read_osp_meta

        # Create invalid .osp/meta.json
        osp_dir = tmp_workspace / ".osp"
        osp_dir.mkdir(parents=True)
        meta_path = osp_dir / "meta.json"
        meta_path.write_text("not valid json {{{", encoding="utf-8")

        result = read_osp_meta(tmp_workspace)
        assert result is None

    def test_read_osp_meta_handles_missing_fields(self, tmp_workspace: Path) -> None:
        """read_osp_meta returns None if required fields are missing."""
        from osp.updater import read_osp_meta

        # Create .osp/meta.json with missing fields
        osp_dir = tmp_workspace / ".osp"
        osp_dir.mkdir(parents=True)
        meta_path = osp_dir / "meta.json"
        meta_path.write_text(json.dumps({"seed_id": "incomplete"}), encoding="utf-8")

        result = read_osp_meta(tmp_workspace)
        assert result is None


class TestWriteOSPMeta:
    """Test the write_osp_meta function in generator.py."""

    def test_write_osp_meta_creates_osp_directory(self, tmp_workspace: Path, sample_seed: Seed) -> None:
        """write_osp_meta creates .osp directory if it doesn't exist."""
        from osp.generator import write_osp_meta

        meta_path = write_osp_meta(tmp_workspace, sample_seed, "test_seed")
        assert meta_path.exists()
        assert meta_path.parent.name == ".osp"

    def test_write_osp_meta_creates_valid_json(self, tmp_workspace: Path, sample_seed: Seed) -> None:
        """write_osp_meta creates valid JSON file."""
        from osp.generator import write_osp_meta

        meta_path = write_osp_meta(tmp_workspace, sample_seed, "test_seed")

        with open(meta_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert data["seed_id"] == "test_001"
        assert data["seed_name"] == "Test Soul"
        assert data["seed_file"] == "test_seed"
        assert data["installed_version"] == 1.0
        assert "installed_at" in data
        assert "osp_version" in data

    def test_write_osp_meta_includes_current_osp_version(self, tmp_workspace: Path, sample_seed: Seed) -> None:
        """write_osp_meta includes current OSP version."""
        from osp.generator import write_osp_meta
        import osp

        meta_path = write_osp_meta(tmp_workspace, sample_seed, "test_seed")

        with open(meta_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert data["osp_version"] == osp.__version__

    def test_write_osp_meta_includes_iso_timestamp(self, tmp_workspace: Path, sample_seed: Seed) -> None:
        """write_osp_meta includes ISO format timestamp."""
        from osp.generator import write_osp_meta

        meta_path = write_osp_meta(tmp_workspace, sample_seed, "test_seed")

        with open(meta_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Should contain ISO-like timestamp (e.g., "2024-01-15T10:30:00")
        installed_at = data["installed_at"]
        assert "T" in installed_at or "-" in installed_at


class TestInitWorkspaceWithMeta:
    """Test that init_workspace creates .osp/meta.json."""

    def test_init_workspace_creates_osp_meta(self, tmp_workspace: Path) -> None:
        """init_workspace creates .osp/meta.json along with workspace files."""
        from osp.generator import init_workspace

        init_workspace("tabula_rasa", tmp_workspace)

        meta_path = tmp_workspace / ".osp" / "meta.json"
        assert meta_path.exists()

        with open(meta_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert data["seed_id"] == "tabula_rasa_001"
        assert data["seed_name"] == "The Observer"
        assert "installed_version" in data
        assert "installed_at" in data
        assert "osp_version" in data

    def test_init_workspace_meta_matches_seed(self, tmp_workspace: Path) -> None:
        """init_workspace meta matches the installed seed's metadata."""
        from osp.generator import init_workspace

        init_workspace("glitch", tmp_workspace)

        meta_path = tmp_workspace / ".osp" / "meta.json"
        with open(meta_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert data["seed_id"] == "glitch_001"
        assert data["seed_name"] == "The Glitch"


# === Phase 3: Update Pipeline Tests ===


class TestFileChange:
    """Test the FileChange frozen dataclass."""

    def test_create_file_change(self) -> None:
        """FileChange can be created with all required fields."""
        from osp.updater import FileChange

        change = FileChange(
            filename="SOUL.md",
            action="overwritten",
            details="Updated with new drives",
        )
        assert change.filename == "SOUL.md"
        assert change.action == "overwritten"
        assert change.details == "Updated with new drives"

    def test_file_change_is_frozen(self) -> None:
        """FileChange is immutable."""
        from osp.updater import FileChange

        change = FileChange(
            filename="SOUL.md",
            action="preserved",
            details="Local changes kept",
        )
        with pytest.raises(AttributeError):
            change.filename = "OTHER.md"  # type: ignore[misc]


class TestUpdateResult:
    """Test the UpdateResult frozen dataclass."""

    def test_create_update_result(self) -> None:
        """UpdateResult can be created with all required fields."""
        from osp.updater import FileChange, UpdateResult

        changes = (
            FileChange("SOUL.md", "smart_merged", "Preserved local drives"),
            FileChange("IDENTITY.md", "overwritten", "Updated identity"),
        )
        result = UpdateResult(
            success=True,
            from_version=1.0,
            to_version=2.0,
            changes=changes,
            backup_path="/path/to/backup",
            conflicts=(),
        )
        assert result.success is True
        assert result.from_version == 1.0
        assert result.to_version == 2.0
        assert len(result.changes) == 2
        assert result.backup_path == "/path/to/backup"
        assert result.conflicts == ()

    def test_update_result_is_frozen(self) -> None:
        """UpdateResult is immutable."""
        from osp.updater import UpdateResult

        result = UpdateResult(
            success=True,
            from_version=1.0,
            to_version=2.0,
            changes=(),
            backup_path=None,
            conflicts=(),
        )
        with pytest.raises(AttributeError):
            result.success = False  # type: ignore[misc]

    def test_update_result_with_conflicts(self) -> None:
        """UpdateResult can record conflicts."""
        from osp.updater import UpdateResult

        result = UpdateResult(
            success=True,
            from_version=1.0,
            to_version=2.0,
            changes=(),
            backup_path=None,
            conflicts=("MEMORY.md modified externally",),
        )
        assert len(result.conflicts) == 1


class TestGetFileStrategy:
    """Test the get_file_strategy function."""

    def test_identity_md_uses_overwrite(self) -> None:
        """IDENTITY.md should use OVERWRITE strategy."""
        from osp.merger import MergeStrategy
        from osp.updater import get_file_strategy

        assert get_file_strategy("IDENTITY.md") == MergeStrategy.OVERWRITE

    def test_bootstrap_md_uses_overwrite(self) -> None:
        """BOOTSTRAP.md should use OVERWRITE strategy."""
        from osp.merger import MergeStrategy
        from osp.updater import get_file_strategy

        assert get_file_strategy("BOOTSTRAP.md") == MergeStrategy.OVERWRITE

    def test_heartbeat_md_uses_overwrite(self) -> None:
        """HEARTBEAT.md should use OVERWRITE strategy."""
        from osp.merger import MergeStrategy
        from osp.updater import get_file_strategy

        assert get_file_strategy("HEARTBEAT.md") == MergeStrategy.OVERWRITE

    def test_soul_md_uses_smart_merge(self) -> None:
        """SOUL.md should use SMART_MERGE strategy."""
        from osp.merger import MergeStrategy
        from osp.updater import get_file_strategy

        assert get_file_strategy("SOUL.md") == MergeStrategy.SMART_MERGE

    def test_story_md_uses_section_merge(self) -> None:
        """STORY.md should use SECTION_MERGE strategy."""
        from osp.merger import MergeStrategy
        from osp.updater import get_file_strategy

        assert get_file_strategy("STORY.md") == MergeStrategy.SECTION_MERGE

    def test_agents_md_uses_union_merge(self) -> None:
        """AGENTS.md should use UNION_MERGE strategy."""
        from osp.merger import MergeStrategy
        from osp.updater import get_file_strategy

        assert get_file_strategy("AGENTS.md") == MergeStrategy.UNION_MERGE

    def test_memory_md_uses_preserve(self) -> None:
        """MEMORY.md should use PRESERVE strategy."""
        from osp.merger import MergeStrategy
        from osp.updater import get_file_strategy

        assert get_file_strategy("MEMORY.md") == MergeStrategy.PRESERVE

    def test_user_md_uses_preserve(self) -> None:
        """USER.md should use PRESERVE strategy."""
        from osp.merger import MergeStrategy
        from osp.updater import get_file_strategy

        assert get_file_strategy("USER.md") == MergeStrategy.PRESERVE

    def test_evolution_log_md_uses_preserve(self) -> None:
        """EVOLUTION_LOG.md should use PRESERVE strategy."""
        from osp.merger import MergeStrategy
        from osp.updater import get_file_strategy

        assert get_file_strategy("EVOLUTION_LOG.md") == MergeStrategy.PRESERVE

    def test_boot_md_uses_smart_merge(self) -> None:
        """BOOT.md should use SMART_MERGE strategy."""
        from osp.merger import MergeStrategy
        from osp.updater import get_file_strategy

        assert get_file_strategy("BOOT.md") == MergeStrategy.SMART_MERGE

    def test_unknown_file_returns_preserve(self) -> None:
        """Unknown files should default to PRESERVE strategy."""
        from osp.merger import MergeStrategy
        from osp.updater import get_file_strategy

        assert get_file_strategy("UNKNOWN.md") == MergeStrategy.PRESERVE


class TestCreateBackup:
    """Test the create_backup function."""

    def test_creates_backup_directory(self, tmp_workspace: Path) -> None:
        """create_backup creates .osp/backups/{timestamp}/ directory."""
        from osp.updater import create_backup

        # Create some workspace files
        tmp_workspace.mkdir(parents=True, exist_ok=True)
        (tmp_workspace / "SOUL.md").write_text("# Soul", encoding="utf-8")
        (tmp_workspace / "MEMORY.md").write_text("# Memory", encoding="utf-8")

        backup_path = create_backup(tmp_workspace)

        assert backup_path.exists()
        assert backup_path.parent.name == "backups"
        assert backup_path.parent.parent.name == ".osp"

    def test_copies_md_files_to_backup(self, tmp_workspace: Path) -> None:
        """create_backup copies all .md files to backup directory."""
        from osp.updater import create_backup

        # Create workspace files
        tmp_workspace.mkdir(parents=True, exist_ok=True)
        (tmp_workspace / "SOUL.md").write_text("# Soul content", encoding="utf-8")
        (tmp_workspace / "MEMORY.md").write_text("# Memory content", encoding="utf-8")
        (tmp_workspace / "IDENTITY.md").write_text("# Identity", encoding="utf-8")

        backup_path = create_backup(tmp_workspace)

        # Check files were copied
        assert (backup_path / "SOUL.md").exists()
        assert (backup_path / "MEMORY.md").exists()
        assert (backup_path / "IDENTITY.md").exists()

        # Check content was preserved
        assert (backup_path / "SOUL.md").read_text() == "# Soul content"
        assert (backup_path / "MEMORY.md").read_text() == "# Memory content"

    def test_ignores_non_md_files(self, tmp_workspace: Path) -> None:
        """create_backup only copies .md files, ignores others."""
        from osp.updater import create_backup

        tmp_workspace.mkdir(parents=True, exist_ok=True)
        (tmp_workspace / "SOUL.md").write_text("# Soul", encoding="utf-8")
        (tmp_workspace / "config.json").write_text("{}", encoding="utf-8")
        (tmp_workspace / "data.txt").write_text("data", encoding="utf-8")

        backup_path = create_backup(tmp_workspace)

        assert (backup_path / "SOUL.md").exists()
        assert not (backup_path / "config.json").exists()
        assert not (backup_path / "data.txt").exists()

    def test_handles_empty_workspace(self, tmp_workspace: Path) -> None:
        """create_backup handles workspace with no files."""
        from osp.updater import create_backup

        tmp_workspace.mkdir(parents=True, exist_ok=True)

        backup_path = create_backup(tmp_workspace)

        assert backup_path.exists()
        # Backup directory exists but is empty
        assert list(backup_path.glob("*.md")) == []

    def test_backup_path_contains_timestamp(self, tmp_workspace: Path) -> None:
        """Backup path should contain a timestamp-like component."""
        import re
        from osp.updater import create_backup

        tmp_workspace.mkdir(parents=True, exist_ok=True)
        (tmp_workspace / "SOUL.md").write_text("# Soul", encoding="utf-8")

        backup_path = create_backup(tmp_workspace)

        # Path should contain something that looks like a timestamp
        # e.g., "2024-01-15T10-30-00" or similar
        path_str = str(backup_path.name)
        # Should have at least some digits for timestamp
        assert re.search(r"\d", path_str) is not None


class TestUpdateFile:
    """Test the update_file function."""

    def test_overwrite_strategy_replaces_file(self, tmp_workspace: Path) -> None:
        """OVERWRITE strategy completely replaces the file."""
        from osp.merger import MergeStrategy
        from osp.updater import update_file

        tmp_workspace.mkdir(parents=True, exist_ok=True)
        (tmp_workspace / "IDENTITY.md").write_text("Old content", encoding="utf-8")

        upstream = "New content from upstream"
        change = update_file(tmp_workspace, "IDENTITY.md", upstream, MergeStrategy.OVERWRITE)

        assert change.action == "overwritten"
        assert (tmp_workspace / "IDENTITY.md").read_text() == upstream

    def test_preserve_strategy_keeps_local(self, tmp_workspace: Path) -> None:
        """PRESERVE strategy keeps local file unchanged."""
        from osp.merger import MergeStrategy
        from osp.updater import update_file

        tmp_workspace.mkdir(parents=True, exist_ok=True)
        local_content = "Local user content"
        (tmp_workspace / "MEMORY.md").write_text(local_content, encoding="utf-8")

        upstream = "New content from upstream"
        change = update_file(tmp_workspace, "MEMORY.md", upstream, MergeStrategy.PRESERVE)

        assert change.action == "preserved"
        assert (tmp_workspace / "MEMORY.md").read_text() == local_content

    def test_preserve_strategy_creates_if_not_exists(self, tmp_workspace: Path) -> None:
        """PRESERVE strategy creates file if it doesn't exist locally."""
        from osp.merger import MergeStrategy
        from osp.updater import update_file

        tmp_workspace.mkdir(parents=True, exist_ok=True)

        upstream = "New content"
        change = update_file(tmp_workspace, "MEMORY.md", upstream, MergeStrategy.PRESERVE)

        # When no local file, should use upstream
        assert change.action == "overwritten"
        assert (tmp_workspace / "MEMORY.md").read_text() == upstream

    def test_smart_merge_strategy_merges_soul_md(self, tmp_workspace: Path) -> None:
        """SMART_MERGE strategy uses merge_soul_md for SOUL.md."""
        from osp.merger import MergeStrategy
        from osp.updater import update_file

        tmp_workspace.mkdir(parents=True, exist_ok=True)
        local = "### Curiosity (0.9)\n\nLocal desc."
        (tmp_workspace / "SOUL.md").write_text(local, encoding="utf-8")

        upstream = "### Curiosity (0.5)\n\nUpstream desc."
        change = update_file(tmp_workspace, "SOUL.md", upstream, MergeStrategy.SMART_MERGE)

        assert change.action == "smart_merged"
        # Should preserve local drive value
        content = (tmp_workspace / "SOUL.md").read_text()
        assert "### Curiosity (0.9)" in content

    def test_union_merge_strategy_merges_agents_md(self, tmp_workspace: Path) -> None:
        """UNION_MERGE strategy uses merge_agents_md for AGENTS.md."""
        from osp.merger import MergeStrategy
        from osp.updater import update_file

        tmp_workspace.mkdir(parents=True, exist_ok=True)
        local = "- `fs.read`\n- `local.skill`"
        (tmp_workspace / "AGENTS.md").write_text(local, encoding="utf-8")

        upstream = "- `fs.read`\n- `upstream.skill`"
        change = update_file(tmp_workspace, "AGENTS.md", upstream, MergeStrategy.UNION_MERGE)

        assert change.action == "union_merged"
        # Should contain both skills
        content = (tmp_workspace / "AGENTS.md").read_text()
        assert "`local.skill`" in content
        assert "`upstream.skill`" in content

    def test_section_merge_strategy_merges_story_md(self, tmp_workspace: Path) -> None:
        """SECTION_MERGE strategy uses merge_story_md for STORY.md."""
        from osp.merger import MergeStrategy
        from osp.updater import update_file

        tmp_workspace.mkdir(parents=True, exist_ok=True)
        local = "## Our Story\n\nLocal story content."
        (tmp_workspace / "STORY.md").write_text(local, encoding="utf-8")

        upstream = "## Who I Am\n\nBio.\n\n## Our Story\n\nDefault story."
        change = update_file(tmp_workspace, "STORY.md", upstream, MergeStrategy.SECTION_MERGE)

        assert change.action == "section_merged"
        # Should preserve local Our Story
        content = (tmp_workspace / "STORY.md").read_text()
        assert "Local story content." in content

    def test_skips_empty_upstream(self, tmp_workspace: Path) -> None:
        """update_file skips files with empty upstream content."""
        from osp.merger import MergeStrategy
        from osp.updater import update_file

        tmp_workspace.mkdir(parents=True, exist_ok=True)
        (tmp_workspace / "STORY.md").write_text("Local content", encoding="utf-8")

        change = update_file(tmp_workspace, "STORY.md", "", MergeStrategy.OVERWRITE)

        assert change.action == "skipped"


class TestUpdateWorkspace:
    """Test the update_workspace function - the main entry point."""

    @pytest.fixture
    def initialized_workspace(self, tmp_workspace: Path) -> Path:
        """Create a workspace initialized with tabula_rasa seed."""
        from osp.generator import init_workspace

        init_workspace("tabula_rasa", tmp_workspace)
        return tmp_workspace

    def test_update_returns_success_when_newer_version(
        self, initialized_workspace: Path
    ) -> None:
        """update_workspace returns success when updating to newer version."""
        from osp.updater import update_workspace

        # First, modify the meta to have an old version
        import json
        meta_path = initialized_workspace / ".osp" / "meta.json"
        with open(meta_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        data["installed_version"] = 0.5  # Old version
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(data, f)

        result = update_workspace(initialized_workspace)

        assert result.success is True
        assert result.from_version == 0.5
        assert result.to_version > 0.5

    def test_update_creates_backup(self, initialized_workspace: Path) -> None:
        """update_workspace creates backup before modifying files."""
        from osp.updater import update_workspace

        # Modify local file to ensure it's backed up
        soul_path = initialized_workspace / "SOUL.md"
        original_content = soul_path.read_text()
        modified_content = original_content.replace("0.5", "0.9")  # Change drive value
        soul_path.write_text(modified_content, encoding="utf-8")

        result = update_workspace(initialized_workspace)

        assert result.backup_path is not None
        backup_dir = Path(result.backup_path)
        assert backup_dir.exists()

    def test_update_preserves_memory_md(self, initialized_workspace: Path) -> None:
        """update_workspace preserves MEMORY.md (PRESERVE strategy)."""
        from osp.updater import update_workspace

        # Modify MEMORY.md
        memory_path = initialized_workspace / "MEMORY.md"
        original_content = "Modified local memory content."
        memory_path.write_text(original_content, encoding="utf-8")

        result = update_workspace(initialized_workspace)

        # MEMORY.md should still have local content
        assert memory_path.read_text() == original_content
        # Check change record
        memory_changes = [c for c in result.changes if c.filename == "MEMORY.md"]
        assert len(memory_changes) == 1
        assert memory_changes[0].action == "preserved"

    def test_update_overwrites_identity_md(self, initialized_workspace: Path) -> None:
        """update_workspace overwrites IDENTITY.md (OVERWRITE strategy)."""
        from osp.updater import update_workspace

        identity_path = initialized_workspace / "IDENTITY.md"
        original_content = identity_path.read_text()

        result = update_workspace(initialized_workspace)

        # Check change record
        identity_changes = [c for c in result.changes if c.filename == "IDENTITY.md"]
        assert len(identity_changes) == 1
        assert identity_changes[0].action == "overwritten"

    def test_update_preserves_local_drive_values(
        self, initialized_workspace: Path
    ) -> None:
        """update_workspace preserves local drive values in SOUL.md."""
        from osp.updater import update_workspace

        # Modify drive values in SOUL.md
        soul_path = initialized_workspace / "SOUL.md"
        content = soul_path.read_text()
        # Change a drive value (tabula_rasa has curiosity: 0.8)
        modified_content = content.replace("### Curiosity (0.8)", "### Curiosity (0.95)")
        soul_path.write_text(modified_content, encoding="utf-8")

        result = update_workspace(initialized_workspace)

        # Drive value should be preserved
        updated_content = soul_path.read_text()
        assert "### Curiosity (0.95)" in updated_content

        # Check change record
        soul_changes = [c for c in result.changes if c.filename == "SOUL.md"]
        assert len(soul_changes) == 1
        assert soul_changes[0].action == "smart_merged"

    def test_update_with_dry_run_does_not_modify(
        self, initialized_workspace: Path
    ) -> None:
        """update_workspace with dry_run=True does not modify files."""
        from osp.updater import update_workspace

        soul_path = initialized_workspace / "SOUL.md"
        original_content = soul_path.read_text()

        result = update_workspace(initialized_workspace, dry_run=True)

        # Files should be unchanged
        assert soul_path.read_text() == original_content
        # No backup should be created
        assert result.backup_path is None
        # Should still be successful (simulation)
        assert result.success is True

    def test_update_with_force_creates_if_no_meta(
        self, tmp_workspace: Path
    ) -> None:
        """update_workspace with force=True creates workspace if no meta."""
        from osp.updater import update_workspace

        # Create workspace without meta
        tmp_workspace.mkdir(parents=True, exist_ok=True)
        (tmp_workspace / "SOUL.md").write_text("# Local file", encoding="utf-8")

        result = update_workspace(tmp_workspace, seed_name="tabula_rasa", force=True)

        assert result.success is True
        # Meta should now exist
        assert (tmp_workspace / ".osp" / "meta.json").exists()

    def test_update_fails_without_meta_and_no_force(
        self, tmp_workspace: Path
    ) -> None:
        """update_workspace fails if no meta and force=False."""
        from osp.updater import update_workspace

        tmp_workspace.mkdir(parents=True, exist_ok=True)

        result = update_workspace(tmp_workspace)

        assert result.success is False
        assert len(result.conflicts) > 0

    def test_update_with_specific_seed_name(
        self, initialized_workspace: Path
    ) -> None:
        """update_workspace can use a specific seed name instead of meta."""
        from osp.updater import update_workspace

        result = update_workspace(initialized_workspace, seed_name="glitch")

        assert result.success is True
        # Check that IDENTITY.md now contains "The Glitch"
        identity = (initialized_workspace / "IDENTITY.md").read_text()
        assert "The Glitch" in identity

    def test_update_updates_meta_version(
        self, initialized_workspace: Path
    ) -> None:
        """update_workspace updates the meta.json version."""
        import json
        from osp.updater import update_workspace

        # Set old version
        meta_path = initialized_workspace / ".osp" / "meta.json"
        with open(meta_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        data["installed_version"] = 0.5
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(data, f)

        result = update_workspace(initialized_workspace)

        # Check meta was updated
        with open(meta_path, "r", encoding="utf-8") as f:
            updated_data = json.load(f)

        assert updated_data["installed_version"] == result.to_version

    def test_update_handles_nonexistent_seed(
        self, initialized_workspace: Path
    ) -> None:
        """update_workspace handles nonexistent seed gracefully."""
        from osp.updater import update_workspace

        result = update_workspace(initialized_workspace, seed_name="nonexistent_seed")

        assert result.success is False
        assert len(result.conflicts) > 0
