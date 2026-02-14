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

class TestGenerateWorkspace:
    def test_generates_all_files(self, sample_seed: Seed) -> None:
        workspace = generate_workspace(sample_seed)
        assert set(workspace.keys()) == set(TEMPLATE_REGISTRY.keys())

    def test_all_files_are_nonempty_strings(self, sample_seed: Seed) -> None:
        workspace = generate_workspace(sample_seed)
        for filename, content in workspace.items():
            assert isinstance(content, str), f"{filename} is not a string"
            assert len(content) > 0, f"{filename} is empty"

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


# === File Writing ===

class TestInitWorkspace:
    def test_writes_all_files(self, tmp_workspace: Path) -> None:
        written = init_workspace("tabula_rasa", tmp_workspace)
        assert len(written) == len(TEMPLATE_REGISTRY)
        for path in written:
            assert path.exists()
            assert path.stat().st_size > 0

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
