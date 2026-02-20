"""Tests for template rendering functions.

Verifies that each template produces correct, non-empty output.
"""

import pytest

from osp.models import Seed
from osp.templates import (
    render_heartbeat_md,
    render_evolution_log_md,
    render_story_md,
    TEMPLATE_REGISTRY,
)


@pytest.fixture
def sample_seed() -> Seed:
    """A minimal seed for testing."""
    return Seed.from_dict(
        {
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
    )


@pytest.fixture
def seed_with_story() -> Seed:
    """A seed with story content for testing."""
    return Seed.from_dict(
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


# === HEARTBEAT.md Tests ===


class TestRenderHeartbeatMd:
    """Tests for the HEARTBEAT.md evolution template."""

    def test_returns_non_empty_string(self, sample_seed: Seed) -> None:
        """HEARTBEAT.md should always produce non-empty output."""
        result = render_heartbeat_md(sample_seed)
        assert isinstance(result, str)
        assert len(result) > 100

    def test_contains_agent_name(self, sample_seed: Seed) -> None:
        """HEARTBEAT.md should address the agent by name."""
        result = render_heartbeat_md(sample_seed)
        assert "Test Soul" in result

    def test_contains_reflection_protocol(self, sample_seed: Seed) -> None:
        """HEARTBEAT.md should have a reflection protocol section."""
        result = render_heartbeat_md(sample_seed)
        assert "Reflection" in result or "reflection" in result

    def test_contains_accelerated_evolution_hint(self, sample_seed: Seed) -> None:
        """HEARTBEAT.md should hint at faster evolution (0.15 max change per cycle)."""
        result = render_heartbeat_md(sample_seed)
        # Should mention 0.15 or "faster" or "accelerated" or similar
        assert "0.15" in result or "accelerat" in result.lower()

    def test_mission_lock_hides_mission_evolution(self, sample_seed: Seed) -> None:
        """When mission_lock is True, mission evolution section should be hidden."""
        # Create seed with mission_lock=True
        locked_seed = Seed.from_dict(
            {
                "meta": {
                    "seed_id": "test_locked",
                    "name": "Locked Soul",
                    "version": 1.0,
                    "created_at": "2024-01-01",
                },
                "nucleus": {
                    "drives": {"curiosity": 0.5},
                    "prime_directives": ["Be kind."],
                },
                "persona": {
                    "current_mission": "Fixed mission",
                    "mission_lock": True,
                    "memory_summary": "Test",
                    "unlocked_skills": [],
                },
                "pulse": {
                    "tone": ["calm"],
                    "formatting_preference": "text",
                    "quirks": [],
                },
            }
        )
        result = render_heartbeat_md(locked_seed)
        # Mission Evolution section should not appear
        assert "Mission Evolution" not in result


# === EVOLUTION_LOG.md Tests (NEW) ===


class TestRenderEvolutionLogMd:
    """Tests for the new EVOLUTION_LOG.md evolution report template."""

    def test_returns_non_empty_string(self, sample_seed: Seed) -> None:
        """EVOLUTION_LOG.md should always produce non-empty output."""
        result = render_evolution_log_md(sample_seed)
        assert isinstance(result, str)
        assert len(result) > 50

    def test_contains_title(self, sample_seed: Seed) -> None:
        """EVOLUTION_LOG.md should have a clear title."""
        result = render_evolution_log_md(sample_seed)
        assert "# " in result  # Has a heading
        assert "Evolution" in result or "evolution" in result

    def test_contains_template_for_memories(self, sample_seed: Seed) -> None:
        """EVOLUTION_LOG.md should have a section for new memories."""
        result = render_evolution_log_md(sample_seed)
        assert "memor" in result.lower()

    def test_contains_template_for_skills(self, sample_seed: Seed) -> None:
        """EVOLUTION_LOG.md should have a section for unlocked skills."""
        result = render_evolution_log_md(sample_seed)
        assert "skill" in result.lower()

    def test_contains_template_for_drive_changes(self, sample_seed: Seed) -> None:
        """EVOLUTION_LOG.md should have a section for drive changes."""
        result = render_evolution_log_md(sample_seed)
        assert "drive" in result.lower()

    def test_in_template_registry(self) -> None:
        """EVOLUTION_LOG.md should be registered in the template registry."""
        assert "EVOLUTION_LOG.md" in TEMPLATE_REGISTRY


# === STORY.md Evolution Tests (NEW) ===


class TestRenderStoryMdEvolution:
    """Tests for STORY.md with evolution support."""

    def test_story_has_our_story_section(self, seed_with_story: Seed) -> None:
        """STORY.md should have 'Our Story' section for evolution."""
        result = render_story_md(seed_with_story)
        assert "Our Story" in result or "our story" in result.lower()

    def test_story_without_story_returns_empty(self, sample_seed: Seed) -> None:
        """Seeds without story should return empty STORY.md."""
        result = render_story_md(sample_seed)
        assert result == ""

    def test_story_evolution_section_is_appendable(self, seed_with_story: Seed) -> None:
        """STORY.md should indicate the story grows over time."""
        result = render_story_md(seed_with_story)
        # Should mention evolution or growing or appending
        lower = result.lower()
        assert "growing" in lower or "evolv" in lower or "append" in lower or "add" in lower

    def test_story_contains_existing_memories(self, seed_with_story: Seed) -> None:
        """STORY.md should include seed's existing memories."""
        result = render_story_md(seed_with_story)
        assert "First test" in result
        assert "It passed" in result
