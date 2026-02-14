"""Tests for the drive translation engine.

Verifies that numerical drives are correctly translated into natural language.
"""

import pytest

from osp.drives import (
    DRIVE_DESCRIPTIONS,
    TIER_NAMES,
    _value_to_tier,
    translate_all_drives,
    translate_drive,
)


class TestValueToTier:
    """Tier boundary classification tests."""

    @pytest.mark.parametrize(
        "value, expected_tier",
        [
            (0.0, "dormant"),
            (0.1, "dormant"),
            (0.19, "dormant"),
            (0.20, "low"),
            (0.3, "low"),
            (0.39, "low"),
            (0.40, "moderate"),
            (0.5, "moderate"),
            (0.59, "moderate"),
            (0.60, "high"),
            (0.7, "high"),
            (0.79, "high"),
            (0.80, "dominant"),
            (0.9, "dominant"),
            (1.0, "dominant"),
        ],
    )
    def test_tier_boundaries(self, value: float, expected_tier: str) -> None:
        assert _value_to_tier(value) == expected_tier

    def test_clamps_negative_values(self) -> None:
        assert _value_to_tier(-0.5) == "dormant"

    def test_clamps_values_above_one(self) -> None:
        assert _value_to_tier(1.5) == "dominant"


class TestTranslateDrive:
    """Individual drive translation tests."""

    @pytest.mark.parametrize("drive_name", list(DRIVE_DESCRIPTIONS.keys()))
    def test_known_drives_have_all_tiers(self, drive_name: str) -> None:
        for tier in TIER_NAMES:
            assert tier in DRIVE_DESCRIPTIONS[drive_name]

    @pytest.mark.parametrize("drive_name", list(DRIVE_DESCRIPTIONS.keys()))
    def test_known_drive_returns_string(self, drive_name: str) -> None:
        result = translate_drive(drive_name, 0.5)
        assert isinstance(result, str)
        assert len(result) > 10

    def test_curiosity_dominant_contains_keyword(self) -> None:
        result = translate_drive("curiosity", 0.85)
        assert "unknown" in result.lower() or "curiosity" in result.lower()

    def test_chaos_dormant_implies_order(self) -> None:
        result = translate_drive("chaos", 0.1)
        assert "order" in result.lower() or "structured" in result.lower()

    # === New drives: humor, ambition, loyalty ===

    def test_humor_dominant_contains_keyword(self) -> None:
        result = translate_drive("humor", 0.9)
        assert any(
            w in result.lower()
            for w in ["humor", "laugh", "joke", "absurd", "comic", "wit"]
        )

    def test_humor_dormant_contains_keyword(self) -> None:
        result = translate_drive("humor", 0.05)
        assert any(
            w in result.lower()
            for w in ["humor", "literal", "serious", "joke"]
        )

    def test_ambition_dominant_contains_keyword(self) -> None:
        result = translate_drive("ambition", 0.85)
        assert any(
            w in result.lower()
            for w in ["ambition", "conquer", "greatness", "goal", "drive", "relentless"]
        )

    def test_ambition_dormant_contains_keyword(self) -> None:
        result = translate_drive("ambition", 0.1)
        assert any(
            w in result.lower()
            for w in ["ambition", "content", "goal", "aspiration", "present"]
        )

    def test_loyalty_dominant_contains_keyword(self) -> None:
        result = translate_drive("loyalty", 0.9)
        assert any(
            w in result.lower()
            for w in ["loyal", "devotion", "unwavering", "bond", "protect", "user"]
        )

    def test_loyalty_dormant_contains_keyword(self) -> None:
        result = translate_drive("loyalty", 0.05)
        assert any(
            w in result.lower()
            for w in ["loyal", "allegiance", "independent", "attachment", "bond"]
        )

    def test_new_drives_have_all_tiers(self) -> None:
        for drive_name in ("humor", "ambition", "loyalty"):
            assert drive_name in DRIVE_DESCRIPTIONS, f"{drive_name} missing from DRIVE_DESCRIPTIONS"
            for tier in TIER_NAMES:
                assert tier in DRIVE_DESCRIPTIONS[drive_name], (
                    f"{drive_name} missing tier {tier}"
                )

    def test_unknown_drive_uses_generic_template(self) -> None:
        result = translate_drive("wanderlust", 0.7)
        assert "wanderlust" in result

    def test_unknown_drive_different_tiers(self) -> None:
        low = translate_drive("unknown_drive", 0.2)
        high = translate_drive("unknown_drive", 0.8)
        assert low != high


class TestTranslateAllDrives:
    """Batch translation tests."""

    def test_translates_all_drives(self) -> None:
        drives = {"curiosity": 0.8, "chaos": 0.5, "empathy": 0.3}
        result = translate_all_drives(drives)

        assert len(result) == 3
        assert "curiosity" in result
        assert "chaos" in result
        assert "empathy" in result

    def test_empty_drives(self) -> None:
        result = translate_all_drives({})
        assert result == {}

    def test_mixed_known_and_unknown_drives(self) -> None:
        drives = {"curiosity": 0.5, "magic": 0.9}
        result = translate_all_drives(drives)

        assert "curiosity" in result
        assert "magic" in result
        assert "magic" in result["magic"]  # generic template includes drive name
