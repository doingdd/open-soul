"""Frozen dataclasses representing the OSP seed structure.

Each model is immutable by design - seeds are data, not mutable state.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class OSPMeta:
    """Workspace metadata for tracking seed version.

    Stored in .osp/meta.json to enable version tracking and updates.
    """

    seed_id: str
    seed_name: str
    seed_file: str  # The seed file name (e.g., "tabula_rasa") for lookup
    installed_version: float
    installed_at: str
    osp_version: str

    @classmethod
    def from_dict(cls, data: dict) -> OSPMeta:
        """Create OSPMeta from a dictionary.

        Handles version as string or float.
        Handles missing seed_file for backward compatibility.
        """
        return cls(
            seed_id=str(data["seed_id"]),
            seed_name=str(data["seed_name"]),
            seed_file=str(data.get("seed_file", data.get("seed_id", ""))),
            installed_version=float(data["installed_version"]),
            installed_at=str(data["installed_at"]),
            osp_version=str(data["osp_version"]),
        )

    def to_dict(self) -> dict:
        """Serialize OSPMeta to a JSON-compatible dictionary."""
        return {
            "seed_id": self.seed_id,
            "seed_name": self.seed_name,
            "seed_file": self.seed_file,
            "installed_version": self.installed_version,
            "installed_at": self.installed_at,
            "osp_version": self.osp_version,
        }


@dataclass(frozen=True)
class Meta:
    """Seed identity metadata."""

    seed_id: str
    name: str
    version: float
    created_at: str


@dataclass(frozen=True)
class Nucleus:
    """Layer 1: Immutable core - drives and prime directives."""

    drives: dict[str, float]
    prime_directives: list[str]


@dataclass(frozen=True)
class Persona:
    """Layer 2: Evolving state - mission, memory, skills."""

    current_mission: Optional[str]
    mission_lock: bool
    memory_summary: str
    unlocked_skills: list[str]


@dataclass(frozen=True)
class Pulse:
    """Layer 3: Expression style - tone, format, quirks."""

    tone: list[str]
    formatting_preference: str
    quirks: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class Story:
    """Optional pre-written story content for instant-ready characters.

    When provided, these fields are used directly instead of requiring
    LLM-based evolution. This follows Clawra's approach: hand-written
    stories have more soul than generated ones.
    """

    age: Optional[int] = None
    location: Optional[str] = None
    occupation: Optional[str] = None
    biography: Optional[str] = None
    daily_routine: Optional[str] = None
    memories: Optional[list[dict]] = None
    speech_examples: Optional[list[str]] = None


@dataclass(frozen=True)
class Seed:
    """Complete soul seed - the DNA of an AI agent."""

    meta: Meta
    nucleus: Nucleus
    persona: Persona
    pulse: Pulse
    story: Optional[Story] = None  # Pre-written story (optional)

    @classmethod
    def from_dict(cls, data: dict) -> Seed:
        """Create a Seed from a raw YAML dictionary.

        Raises:
            KeyError: If required fields are missing.
            TypeError: If field types are incorrect.
        """
        meta = Meta(
            seed_id=data["meta"]["seed_id"],
            name=data["meta"]["name"],
            version=float(data["meta"]["version"]),
            created_at=str(data["meta"]["created_at"]),
        )

        nucleus = Nucleus(
            drives=dict(data["nucleus"]["drives"]),
            prime_directives=list(data["nucleus"]["prime_directives"]),
        )

        persona_data = data["persona"]
        persona = Persona(
            current_mission=persona_data.get("current_mission"),
            mission_lock=bool(persona_data.get("mission_lock", False)),
            memory_summary=str(persona_data.get("memory_summary", "")),
            unlocked_skills=list(persona_data.get("unlocked_skills", [])),
        )

        pulse_data = data["pulse"]
        pulse = Pulse(
            tone=list(pulse_data.get("tone", [])),
            formatting_preference=str(pulse_data.get("formatting_preference", "markdown")),
            quirks=list(pulse_data.get("quirks", [])),
        )

        # Parse optional story
        story = None
        if "story" in data and data["story"]:
            story_data = data["story"]
            story = Story(
                age=story_data.get("age"),
                location=story_data.get("location"),
                occupation=story_data.get("occupation"),
                biography=story_data.get("biography"),
                daily_routine=story_data.get("daily_routine"),
                memories=list(story_data.get("memories", [])) if story_data.get("memories") else None,
                speech_examples=list(story_data.get("speech_examples", [])) if story_data.get("speech_examples") else None,
            )

        return cls(meta=meta, nucleus=nucleus, persona=persona, pulse=pulse, story=story)
