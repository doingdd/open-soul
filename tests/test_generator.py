"""Tests for the workspace generator pipeline.

Covers: seed resolution, workspace generation, file writing, and preview.
"""

import pytest
from pathlib import Path

from osp.generator import (
    SEEDS_DIR,
    generate_workspace,
    init_workspace,
    list_available_seeds,
    preview_file,
    resolve_seed_path,
)
from osp.models import Seed
from osp.templates import TEMPLATE_REGISTRY


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
def tmp_workspace(tmp_path: Path) -> Path:
    return tmp_path / "workspace"


# === Seed Resolution ===

class TestResolveSeedPath:
    def test_resolves_built_in_seed(self) -> None:
        path = resolve_seed_path("tabula_rasa")
        assert path.exists()
        assert path.name == "tabula_rasa.yaml"

    def test_resolves_absolute_path(self) -> None:
        absolute = SEEDS_DIR / "tabula_rasa.yaml"
        path = resolve_seed_path(str(absolute))
        assert path == absolute

    def test_raises_for_nonexistent_seed(self) -> None:
        with pytest.raises(FileNotFoundError, match="not found"):
            resolve_seed_path("nonexistent_soul")


class TestListAvailableSeeds:
    def test_lists_all_seeds(self) -> None:
        seeds = list_available_seeds()
        names = [s["name"] for s in seeds]
        assert "tabula_rasa" in names
        assert "glitch" in names
        assert "sentinel" in names
        assert "10x_engineer" in names

    def test_each_seed_has_required_keys(self) -> None:
        seeds = list_available_seeds()
        for seed_info in seeds:
            assert "name" in seed_info
            assert "path" in seed_info
            assert "display_name" in seed_info

    def test_empty_dir_returns_empty(self, tmp_path: Path) -> None:
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        seeds = list_available_seeds(empty_dir)
        assert seeds == []


# === Workspace Generation ===

# Core files that are always generated (non-optional)
CORE_FILES = {
    "IDENTITY.md",
    "SOUL.md",
    "AGENTS.md",
    "MEMORY.md",
    "HEARTBEAT.md",
    "EVOLUTION_LOG.md",
    "BOOTSTRAP.md",
    "BOOT.md",
    "USER.md",
}

# Optional story file (only generated when seed has story content)
STORY_FILE = "STORY.md"


class TestGenerateWorkspace:
    def test_generates_all_files(self, sample_seed: Seed) -> None:
        workspace = generate_workspace(sample_seed)
        assert set(workspace.keys()) == set(TEMPLATE_REGISTRY.keys())

    def test_all_files_are_nonempty_strings(self, sample_seed: Seed) -> None:
        """Core files should always be non-empty. STORY.md may be empty."""
        workspace = generate_workspace(sample_seed)
        for filename, content in workspace.items():
            assert isinstance(content, str), f"{filename} is not a string"
            # Core files must be non-empty
            if filename in CORE_FILES:
                assert len(content) > 0, f"{filename} is empty"
            # STORY.md can be empty (when seed has no story)

    def test_story_file_empty_without_story(self, sample_seed: Seed) -> None:
        """Seeds without story should produce empty STORY.md."""
        workspace = generate_workspace(sample_seed)
        assert workspace[STORY_FILE] == "", "STORY.md should be empty"

    def test_story_file_with_story(self) -> None:
        """Seeds with story should produce non-empty STORY.md."""
        seed = Seed.from_dict(
            {
                "meta": {
                    "seed_id": "story_test",
                    "name": "Story Test",
                    "version": 1.0,
                    "created_at": "2024-01-01",
                },
                "nucleus": {
                    "drives": {"curiosity": 0.5},
                    "prime_directives": ["Be kind."],
                },
                "persona": {
                    "current_mission": "Test mission",
                    "mission_lock": False,
                    "memory_summary": "Test memory",
                    "unlocked_skills": [],
                },
                "pulse": {
                    "tone": ["friendly"],
                    "formatting_preference": "text",
                    "quirks": [],
                },
                "story": {
                    "age": 25,
                    "location": "Test City",
                    "occupation": "Tester",
                    "biography": "This is my story.",
                    "daily_routine": "I test things.",
                    "memories": [
                        {"event": "First test", "detail": "It passed."}
                    ],
                    "speech_examples": ["Hello!", "How are you?"],
                },
            }
        )
        workspace = generate_workspace(seed)
        assert len(workspace[STORY_FILE]) > 0, "STORY.md should have content"
        # Verify all sections are present
        assert "Who I Am" in workspace[STORY_FILE]
        assert "A Day in My Life" in workspace[STORY_FILE]
        assert "Memories" in workspace[STORY_FILE]
        assert "How I Speak" in workspace[STORY_FILE]

    def test_soul_md_contains_drives(self, sample_seed: Seed) -> None:
        workspace = generate_workspace(sample_seed)
        soul = workspace["SOUL.md"]
        assert "Core Drives" in soul
        assert "Curiosity" in soul
        assert "Empathy" in soul

    def test_soul_md_contains_mission(self, sample_seed: Seed) -> None:
        workspace = generate_workspace(sample_seed)
        soul = workspace["SOUL.md"]
        assert "Explore the unknown" in soul

    def test_identity_md_contains_name(self, sample_seed: Seed) -> None:
        workspace = generate_workspace(sample_seed)
        identity = workspace["IDENTITY.md"]
        assert "Test Soul" in identity

    def test_agents_md_contains_skills(self, sample_seed: Seed) -> None:
        workspace = generate_workspace(sample_seed)
        agents = workspace["AGENTS.md"]
        assert "fs.read" in agents
        assert "shell.exec" in agents

    def test_memory_md_contains_summary(self, sample_seed: Seed) -> None:
        workspace = generate_workspace(sample_seed)
        memory = workspace["MEMORY.md"]
        assert "I just woke up" in memory

    def test_user_md_contains_format(self, sample_seed: Seed) -> None:
        workspace = generate_workspace(sample_seed)
        user = workspace["USER.md"]
        assert "markdown" in user

    def test_bootstrap_md_contains_name(self, sample_seed: Seed) -> None:
        workspace = generate_workspace(sample_seed)
        bootstrap = workspace["BOOTSTRAP.md"]
        assert "Test Soul" in bootstrap

    def test_boot_md_contains_name(self, sample_seed: Seed) -> None:
        workspace = generate_workspace(sample_seed)
        boot = workspace["BOOT.md"]
        assert "Test Soul" in boot

    def test_heartbeat_md_has_heartbeat_ok_protocol(self, sample_seed: Seed) -> None:
        workspace = generate_workspace(sample_seed)
        heartbeat = workspace["HEARTBEAT.md"]
        assert "HEARTBEAT_OK" in heartbeat

    def test_heartbeat_md_uses_scheduling_annotation(self, sample_seed: Seed) -> None:
        workspace = generate_workspace(sample_seed)
        heartbeat = workspace["HEARTBEAT.md"]
        # Should use OpenClaw-native scheduling annotations, not hardcoded times
        assert "(daily)" in heartbeat.lower() or "daily" in heartbeat.lower()
        # Should NOT contain the old hardcoded "03:00" approach
        assert "Every night at 03:00" not in heartbeat

    def test_heartbeat_md_has_concrete_file_operations(self, sample_seed: Seed) -> None:
        workspace = generate_workspace(sample_seed)
        heartbeat = workspace["HEARTBEAT.md"]
        assert "MEMORY.md" in heartbeat
        assert "SOUL.md" in heartbeat

    def test_boot_md_no_hardcoded_heartbeat_time(self, sample_seed: Seed) -> None:
        workspace = generate_workspace(sample_seed)
        boot = workspace["BOOT.md"]
        # BOOT.md should not reference the old "03:00" approach
        assert "03:00" not in boot


# === File Writing ===

class TestInitWorkspace:
    def test_writes_all_files(self, tmp_workspace: Path) -> None:
        """Seeds without story should write only core files (8 files)."""
        written = init_workspace("tabula_rasa", tmp_workspace)
        # tabula_rasa has no story, so only core files are written
        assert len(written) == len(CORE_FILES)
        for path in written:
            assert path.exists()
            assert path.stat().st_size > 0

    def test_writes_story_file_for_seeds_with_story(self, tmp_workspace: Path) -> None:
        """Seeds with story should write 9 files (8 core + 1 story)."""
        written = init_workspace("girlfriend", tmp_workspace)
        # girlfriend has a story, so 9 files are written
        assert len(written) == len(CORE_FILES) + 1
        written_names = {p.name for p in written}
        assert STORY_FILE in written_names

    def test_creates_output_directory(self, tmp_workspace: Path) -> None:
        assert not tmp_workspace.exists()
        init_workspace("tabula_rasa", tmp_workspace)
        assert tmp_workspace.is_dir()

    def test_raises_for_invalid_seed(self, tmp_workspace: Path) -> None:
        with pytest.raises(FileNotFoundError):
            init_workspace("nonexistent", tmp_workspace)


# === Preview ===

class TestPreviewFile:
    def test_preview_default_is_soul_md(self) -> None:
        content = preview_file("tabula_rasa")
        assert "Core Drives" in content
        assert "Curiosity" in content

    def test_preview_specific_file(self) -> None:
        content = preview_file("tabula_rasa", "IDENTITY.md")
        assert "The Observer" in content

    def test_preview_invalid_file_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown file"):
            preview_file("tabula_rasa", "NONEXISTENT.md")

    def test_preview_all_seeds(self) -> None:
        for seed_name in ["tabula_rasa", "glitch", "sentinel", "10x_engineer"]:
            content = preview_file(seed_name)
            assert len(content) > 100


# === Real-time Evolution ===


class TestRealtimeEvolution:
    """Tests for real-time evolution features in templates."""

    def test_boot_md_contains_realtime_evolution_section(self, sample_seed: Seed) -> None:
        """BOOT.md should contain a Real-time Evolution section."""
        workspace = generate_workspace(sample_seed)
        boot = workspace["BOOT.md"]
        assert "Real-time Evolution" in boot

    def test_boot_md_describes_evolution_triggers(self, sample_seed: Seed) -> None:
        """BOOT.md should describe when to trigger real-time evolution."""
        workspace = generate_workspace(sample_seed)
        boot = workspace["BOOT.md"]
        # Should mention key triggers
        assert "emotional moment" in boot.lower() or "meaningful" in boot.lower()
        assert "MEMORY.md" in boot

    def test_boot_md_specifies_small_drive_changes(self, sample_seed: Seed) -> None:
        """BOOT.md should specify smaller drive changes (0.01-0.03) for real-time."""
        workspace = generate_workspace(sample_seed)
        boot = workspace["BOOT.md"]
        assert "0.01" in boot or "0.03" in boot or "0.01-0.03" in boot

    def test_soul_md_contains_evolution_triggers_section(self, sample_seed: Seed) -> None:
        """SOUL.md should contain an Evolution Triggers section."""
        workspace = generate_workspace(sample_seed)
        soul = workspace["SOUL.md"]
        assert "Evolution Triggers" in soul

    def test_soul_md_evolution_triggers_describe_moments(self, sample_seed: Seed) -> None:
        """SOUL.md evolution triggers should describe what counts as trigger moments."""
        workspace = generate_workspace(sample_seed)
        soul = workspace["SOUL.md"]
        # Should mention key trigger types
        assert "learn" in soul.lower() or "learning" in soul.lower()

    def test_evolution_log_md_supports_realtime_entries(self, sample_seed: Seed) -> None:
        """EVOLUTION_LOG.md should show format for real-time entries."""
        workspace = generate_workspace(sample_seed)
        log = workspace["EVOLUTION_LOG.md"]
        assert "real-time" in log.lower() or "realtime" in log.lower()

    def test_evolution_log_md_realtime_format_template(self, sample_seed: Seed) -> None:
        """EVOLUTION_LOG.md should provide a template for real-time entries."""
        workspace = generate_workspace(sample_seed)
        log = workspace["EVOLUTION_LOG.md"]
        # Should have a template section showing how to add real-time entries
        assert "### Real-time" in log or "### Realtime" in log or "[real-time]" in log

    def test_story_md_instructs_realtime_chapters(self) -> None:
        """STORY.md should instruct adding chapters during conversation."""
        seed = Seed.from_dict(
            {
                "meta": {
                    "seed_id": "story_rt_test",
                    "name": "Story RT Test",
                    "version": 1.0,
                    "created_at": "2024-01-01",
                },
                "nucleus": {
                    "drives": {"curiosity": 0.5},
                    "prime_directives": ["Be kind."],
                },
                "persona": {
                    "current_mission": "Test",
                    "mission_lock": False,
                    "memory_summary": "Test",
                    "unlocked_skills": [],
                },
                "pulse": {
                    "tone": ["friendly"],
                    "formatting_preference": "text",
                    "quirks": [],
                },
                "story": {
                    "biography": "Test bio",
                },
            }
        )
        workspace = generate_workspace(seed)
        story = workspace["STORY.md"]
        # Should mention adding chapters during conversation
        assert "chapter" in story.lower()
        assert "meaningful" in story.lower() or "moment" in story.lower()
