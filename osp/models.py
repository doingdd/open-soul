"""Frozen dataclasses representing the OSP seed structure.

Each model is immutable by design - seeds are data, not mutable state.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


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
class Seed:
    """Complete soul seed - the DNA of an AI agent."""

    meta: Meta
    nucleus: Nucleus
    persona: Persona
    pulse: Pulse

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

        return cls(meta=meta, nucleus=nucleus, persona=persona, pulse=pulse)
