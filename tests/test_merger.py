"""Tests for the merge engine - handling seed updates with user data preservation.

Covers: drive extraction, section merging, skill union, and safe degradation.
"""

import pytest

from osp.merger import (
    MergeStrategy,
    apply_drive_values,
    extract_drive_values,
    extract_our_story_section,
    extract_skills,
    merge_agents_md,
    merge_soul_md,
    merge_story_md,
)


# === MergeStrategy Enum ===


class TestMergeStrategy:
    """Tests for MergeStrategy enum values."""

    def test_has_overwrite_strategy(self) -> None:
        """OVERWRITE strategy should exist."""
        assert MergeStrategy.OVERWRITE.value == "overwrite"

    def test_has_preserve_strategy(self) -> None:
        """PRESERVE strategy should exist."""
        assert MergeStrategy.PRESERVE.value == "preserve"

    def test_has_smart_merge_strategy(self) -> None:
        """SMART_MERGE strategy should exist."""
        assert MergeStrategy.SMART_MERGE.value == "smart_merge"

    def test_has_section_merge_strategy(self) -> None:
        """SECTION_MERGE strategy should exist."""
        assert MergeStrategy.SECTION_MERGE.value == "section_merge"

    def test_has_union_merge_strategy(self) -> None:
        """UNION_MERGE strategy should exist."""
        assert MergeStrategy.UNION_MERGE.value == "union_merge"


# === extract_drive_values ===


class TestExtractDriveValues:
    """Tests for extracting drive values from SOUL.md content."""

    def test_extracts_single_drive(self) -> None:
        """Should extract a single drive with its value."""
        soul_md = """## Core Drives

### Curiosity (0.85)

This drive is very high.
"""
        values = extract_drive_values(soul_md)
        assert values == {"Curiosity": 0.85}

    def test_extracts_multiple_drives(self) -> None:
        """Should extract all drives with their values."""
        soul_md = """## Core Drives

### Curiosity (0.85)

Very curious.

### Empathy (0.5)

Moderate empathy.

### Order (0.0)

Chaos preferred.
"""
        values = extract_drive_values(soul_md)
        assert values == {"Curiosity": 0.85, "Empathy": 0.5, "Order": 0.0}

    def test_handles_varying_whitespace(self) -> None:
        """Should handle different whitespace patterns."""
        soul_md = """## Core Drives

###Curiosity(0.85)
### Empathy(0.5)
### Order (0.0)
"""
        values = extract_drive_values(soul_md)
        assert values == {"Curiosity": 0.85, "Empathy": 0.5, "Order": 0.0}

    def test_handles_multiline_drive_names(self) -> None:
        """Should handle drive names with underscores and spaces."""
        soul_md = """## Core Drives

### Curiosity (0.8)
### Creative_Drive (0.6)
### Social Connection (0.3)
"""
        values = extract_drive_values(soul_md)
        assert values == {
            "Curiosity": 0.8,
            "Creative_Drive": 0.6,
            "Social Connection": 0.3,
        }

    def test_returns_empty_for_no_drives(self) -> None:
        """Should return empty dict if no drives found."""
        soul_md = """# Soul Core

No drives here.
"""
        values = extract_drive_values(soul_md)
        assert values == {}

    def test_returns_empty_for_empty_string(self) -> None:
        """Should return empty dict for empty input."""
        values = extract_drive_values("")
        assert values == {}

    def test_returns_empty_for_none(self) -> None:
        """Should return empty dict for None input (safe degradation)."""
        values = extract_drive_values(None)  # type: ignore
        assert values == {}

    def test_ignores_invalid_values(self) -> None:
        """Should skip entries that don't have valid float values."""
        soul_md = """## Core Drives

### Curiosity (0.85)
### Empathy (invalid)
### Order
"""
        values = extract_drive_values(soul_md)
        assert values == {"Curiosity": 0.85}

    def test_handles_extreme_float_strings(self) -> None:
        """Should handle extreme float strings that might cause parsing issues."""
        soul_md = """## Core Drives

### Curiosity (0.85)
### Empathy (1e308)
### Order (0.5)
"""
        values = extract_drive_values(soul_md)
        assert "Curiosity" in values
        assert "Order" in values
        # Empathy might be inf or very large, both should be clamped to 1.0

    def test_clamps_values_to_valid_range(self) -> None:
        """Should clamp drive values to 0.0-1.0 range."""
        soul_md = """## Core Drives

### Curiosity (1.5)
### Empathy (-0.3)
### Order (0.5)
"""
        values = extract_drive_values(soul_md)
        assert values == {"Curiosity": 1.0, "Empathy": 0.0, "Order": 0.5}


# === apply_drive_values ===


class TestApplyDriveValues:
    """Tests for applying drive values to SOUL.md content."""

    def test_applies_single_value(self) -> None:
        """Should update a single drive value."""
        soul_md = """## Core Drives

### Curiosity (0.5)

Some description.
"""
        result = apply_drive_values(soul_md, {"Curiosity": 0.9})
        assert "### Curiosity (0.9)" in result

    def test_applies_multiple_values(self) -> None:
        """Should update multiple drive values."""
        soul_md = """## Core Drives

### Curiosity (0.5)

Desc.

### Empathy (0.3)

Desc.
"""
        result = apply_drive_values(soul_md, {"Curiosity": 0.8, "Empathy": 0.7})
        assert "### Curiosity (0.8)" in result
        assert "### Empathy (0.7)" in result

    def test_preserves_other_content(self) -> None:
        """Should not modify other parts of the file."""
        soul_md = """# Soul Core

## Core Drives

### Curiosity (0.5)

This is the description.

## Boundaries

- Be honest.
"""
        result = apply_drive_values(soul_md, {"Curiosity": 0.9})
        assert "## Boundaries" in result
        assert "- Be honest." in result
        assert "This is the description." in result

    def test_returns_original_on_empty_values(self) -> None:
        """Should return original content if no values to apply."""
        soul_md = "### Curiosity (0.5)"
        result = apply_drive_values(soul_md, {})
        assert result == soul_md

    def test_returns_original_on_none_content(self) -> None:
        """Should return empty string for None content (safe degradation)."""
        result = apply_drive_values(None, {"Curiosity": 0.9})  # type: ignore
        assert result == ""

    def test_ignores_drives_not_in_content(self) -> None:
        """Should ignore values for drives not present in content."""
        soul_md = "### Curiosity (0.5)"
        result = apply_drive_values(soul_md, {"Empathy": 0.9, "Curiosity": 0.8})
        assert "### Curiosity (0.8)" in result
        assert "Empathy" not in result


# === merge_soul_md ===


class TestMergeSoulMd:
    """Tests for merging SOUL.md files - preserves user drive values."""

    def test_preserves_local_drive_values(self) -> None:
        """Should keep local drive values when merging."""
        local = """## Core Drives

### Curiosity (0.9)

Local desc.

### Empathy (0.8)

Local desc.
"""
        upstream = """## Core Drives

### Curiosity (0.5)

Upstream desc.

### Empathy (0.3)

Upstream desc.
"""
        result = merge_soul_md(local, upstream)
        assert "### Curiosity (0.9)" in result
        assert "### Empathy (0.8)" in result

    def test_uses_upstream_descriptions(self) -> None:
        """Should use upstream descriptions (they may be improved)."""
        local = """## Core Drives

### Curiosity (0.9)

Old local description.
"""
        upstream = """## Core Drives

### Curiosity (0.5)

New improved upstream description.
"""
        result = merge_soul_md(local, upstream)
        assert "New improved upstream description." in result
        assert "Old local description." not in result

    def test_uses_upstream_for_new_drives(self) -> None:
        """Should add new drives from upstream with their values."""
        local = """## Core Drives

### Curiosity (0.9)

Desc.
"""
        upstream = """## Core Drives

### Curiosity (0.5)

Desc.

### Empathy (0.7)

New drive in upstream.
"""
        result = merge_soul_md(local, upstream)
        assert "### Curiosity (0.9)" in result  # Local value preserved
        assert "### Empathy (0.7)" in result  # Upstream value for new drive

    def test_removes_drives_not_in_upstream(self) -> None:
        """Should remove drives that no longer exist in upstream."""
        local = """## Core Drives

### Curiosity (0.9)

Desc.

### OldDrive (0.5)

This drive was removed.
"""
        upstream = """## Core Drives

### Curiosity (0.5)

Desc only.
"""
        result = merge_soul_md(local, upstream)
        assert "### Curiosity (0.9)" in result
        assert "OldDrive" not in result

    def test_handles_empty_local(self) -> None:
        """Should return upstream content if local is empty."""
        local = ""
        upstream = """## Core Drives

### Curiosity (0.5)

Desc.
"""
        result = merge_soul_md(local, upstream)
        assert result == upstream

    def test_handles_empty_upstream(self) -> None:
        """Should return local content if upstream is empty."""
        local = """## Core Drives

### Curiosity (0.9)

Desc.
"""
        upstream = ""
        result = merge_soul_md(local, upstream)
        assert result == local

    def test_handles_none_inputs(self) -> None:
        """Should handle None inputs gracefully."""
        local = "### Curiosity (0.9)"
        upstream = "### Curiosity (0.5)"

        result1 = merge_soul_md(None, upstream)  # type: ignore
        assert result1 == upstream

        result2 = merge_soul_md(local, None)  # type: ignore
        assert result2 == local

        result3 = merge_soul_md(None, None)  # type: ignore
        assert result3 == ""

    def test_preserves_non_drive_sections(self) -> None:
        """Should preserve other sections like Mission, Boundaries."""
        local = """## Core Drives

### Curiosity (0.9)

Desc.

## Mission

My local mission.
"""
        upstream = """## Core Drives

### Curiosity (0.5)

New desc.

## Mission

Updated upstream mission.

## Boundaries

- New boundary.
"""
        result = merge_soul_md(local, upstream)
        # Should use upstream for everything except drive values
        assert "### Curiosity (0.9)" in result  # Local value
        assert "New desc." in result  # Upstream description
        assert "Updated upstream mission." in result  # Upstream mission
        assert "- New boundary." in result  # Upstream boundary


# === extract_our_story_section ===


class TestExtractOurStorySection:
    """Tests for extracting the 'Our Story' section from STORY.md."""

    def test_extracts_our_story_section(self) -> None:
        """Should extract the Our Story section."""
        story_md = """# My Story

## Who I Am

Biography here.

## Our Story

> This grows with every conversation.

**Chapter 1: The Beginning**

> This is where it started.

## Memories

Some memories.
"""
        result = extract_our_story_section(story_md)
        assert result is not None
        assert "## Our Story" in result
        assert "Chapter 1: The Beginning" in result
        assert "## Who I Am" not in result
        assert "## Memories" not in result

    def test_returns_none_if_no_our_story(self) -> None:
        """Should return None if Our Story section doesn't exist."""
        story_md = """# My Story

## Who I Am

Biography here.
"""
        result = extract_our_story_section(story_md)
        assert result is None

    def test_handles_empty_string(self) -> None:
        """Should return None for empty input."""
        result = extract_our_story_section("")
        assert result is None

    def test_handles_none_input(self) -> None:
        """Should return None for None input (safe degradation)."""
        result = extract_our_story_section(None)  # type: ignore
        assert result is None

    def test_extracts_until_next_section(self) -> None:
        """Should extract until the next ## section."""
        story_md = """## Our Story

Our story content.

**Chapter 1: Start**

Beginning.

## Memories

Memory content.
"""
        result = extract_our_story_section(story_md)
        assert result is not None
        assert "Our story content." in result
        assert "**Chapter 1: Start**" in result
        assert "## Memories" not in result

    def test_extracts_until_end_of_file(self) -> None:
        """Should extract until end if Our Story is last section."""
        story_md = """## Who I Am

Bio.

## Our Story

Our story content at the end.
"""
        result = extract_our_story_section(story_md)
        assert result is not None
        assert "Our story content at the end." in result


# === extract_skills ===


class TestExtractSkills:
    """Tests for extracting skill names from AGENTS.md."""

    def test_extracts_single_skill(self) -> None:
        """Should extract a single skill."""
        agents_md = """# Available Tools

- `fs.read`
"""
        skills = extract_skills(agents_md)
        assert skills == {"fs.read"}

    def test_extracts_multiple_skills(self) -> None:
        """Should extract all skills."""
        agents_md = """# Available Tools

- `fs.read`
- `fs.write`
- `shell.exec`
"""
        skills = extract_skills(agents_md)
        assert skills == {"fs.read", "fs.write", "shell.exec"}

    def test_handles_empty_file(self) -> None:
        """Should return empty set for empty content."""
        skills = extract_skills("")
        assert skills == set()

    def test_handles_none_input(self) -> None:
        """Should return empty set for None input (safe degradation)."""
        skills = extract_skills(None)  # type: ignore
        assert skills == set()

    def test_ignores_non_code_blocks(self) -> None:
        """Should only extract skills in backticks."""
        agents_md = """# Available Tools

- `fs.read`
- fs.write (not in backticks)
- `shell.exec`
"""
        skills = extract_skills(agents_md)
        assert skills == {"fs.read", "shell.exec"}

    def test_handles_no_skills_marker(self) -> None:
        """Should handle the 'read_only' default case."""
        agents_md = """# Available Tools

- `read_only` (No external actions available yet)
"""
        skills = extract_skills(agents_md)
        assert skills == {"read_only"}


# === merge_agents_md ===


class TestMergeAgentsMd:
    """Tests for merging AGENTS.md files - union of skills."""

    def test_merges_skills_union(self) -> None:
        """Should combine skills from both local and upstream."""
        local = """# Available Tools

- `fs.read`
- `fs.write`
"""
        upstream = """# Available Tools

- `fs.read`
- `shell.exec`
"""
        result = merge_agents_md(local, upstream)
        assert "`fs.read`" in result
        assert "`fs.write`" in result  # From local
        assert "`shell.exec`" in result  # From upstream

    def test_removes_duplicates(self) -> None:
        """Should not duplicate skills that exist in both."""
        local = """# Available Tools

- `fs.read`
- `fs.write`
"""
        upstream = """# Available Tools

- `fs.read`
- `fs.write`
- `shell.exec`
"""
        result = merge_agents_md(local, upstream)
        # Count occurrences of fs.read
        count = result.count("`fs.read`")
        assert count == 1

    def test_uses_upstream_structure(self) -> None:
        """Should use upstream structure but include local skills."""
        local = """# Available Tools

- `local.skill`
"""
        upstream = """# Available Tools

> Some new header from upstream.

- `upstream.skill`

> Note from upstream.
"""
        result = merge_agents_md(local, upstream)
        assert "`local.skill`" in result
        assert "`upstream.skill`" in result

    def test_handles_empty_local(self) -> None:
        """Should return upstream skills if local is empty."""
        local = ""
        upstream = """# Available Tools

- `fs.read`
"""
        result = merge_agents_md(local, upstream)
        assert "`fs.read`" in result

    def test_handles_empty_upstream(self) -> None:
        """Should return local skills if upstream is empty."""
        local = """# Available Tools

- `fs.read`
"""
        upstream = ""
        result = merge_agents_md(local, upstream)
        assert "`fs.read`" in result

    def test_handles_none_inputs(self) -> None:
        """Should handle None inputs gracefully."""
        local = "- `fs.read`"
        upstream = "- `shell.exec`"

        result1 = merge_agents_md(None, upstream)  # type: ignore
        assert "`shell.exec`" in result1

        result2 = merge_agents_md(local, None)  # type: ignore
        assert "`fs.read`" in result2

        result3 = merge_agents_md(None, None)  # type: ignore
        assert result3 == ""

    def test_removes_read_only_when_real_skills_added(self) -> None:
        """Should remove 'read_only' placeholder when real skills exist."""
        local = """# Available Tools

- `read_only` (No external actions available yet)
"""
        upstream = """# Available Tools

- `fs.read`
"""
        result = merge_agents_md(local, upstream)
        assert "`fs.read`" in result
        assert "read_only" not in result


# === merge_story_md ===


class TestMergeStoryMd:
    """Tests for merging STORY.md files - preserves Our Story section."""

    def test_preserves_local_our_story(self) -> None:
        """Should keep local Our Story section when merging."""
        local = """# My Story

## Who I Am

Local bio.

## Our Story

**Chapter 1: Our Beginning**

> The local story content.

## Memories

Local memories.
"""
        upstream = """# My Story

## Who I Am

Upstream bio (updated).

## Our Story

**Chapter 1: The Beginning**

> Upstream default story.

## Memories

Upstream memories.
"""
        result = merge_story_md(local, upstream)
        assert "**Chapter 1: Our Beginning**" in result
        assert "The local story content." in result

    def test_uses_upstream_for_other_sections(self) -> None:
        """Should use upstream content for non-Our-Story sections."""
        local = """## Who I Am

Old bio.

## Our Story

Local story.
"""
        upstream = """## Who I Am

New updated bio.

## Our Story

Default story.

## Memories

New memories section.
"""
        result = merge_story_md(local, upstream)
        assert "New updated bio." in result
        assert "New memories section." in result

    def test_handles_no_local_our_story(self) -> None:
        """Should use upstream Our Story if local doesn't have one."""
        local = """## Who I Am

Local bio.
"""
        upstream = """## Who I Am

Upstream bio.

## Our Story

Upstream story.
"""
        result = merge_story_md(local, upstream)
        assert "Upstream story." in result

    def test_handles_no_upstream_our_story(self) -> None:
        """Should preserve local Our Story if upstream doesn't have one."""
        local = """## Who I Am

Local bio.

## Our Story

Local story.
"""
        upstream = """## Who I Am

Upstream bio.
"""
        result = merge_story_md(local, upstream)
        assert "Local story." in result

    def test_handles_empty_local(self) -> None:
        """Should return upstream if local is empty."""
        local = ""
        upstream = """## Who I Am

Upstream bio.
"""
        result = merge_story_md(local, upstream)
        assert result == upstream

    def test_handles_empty_upstream(self) -> None:
        """Should return local if upstream is empty."""
        local = """## Who I Am

Local bio.
"""
        upstream = ""
        result = merge_story_md(local, upstream)
        assert result == local

    def test_handles_none_inputs(self) -> None:
        """Should handle None inputs gracefully."""
        local = "## Our Story\n\nLocal story."
        upstream = "## Who I Am\n\nUpstream."

        result1 = merge_story_md(None, upstream)  # type: ignore
        assert "Upstream." in result1

        result2 = merge_story_md(local, None)  # type: ignore
        assert "Local story." in result2

        result3 = merge_story_md(None, None)  # type: ignore
        assert result3 == ""
