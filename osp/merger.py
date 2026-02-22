"""Merge engine for handling seed updates while preserving user data.

This module implements various merge strategies for combining local user
modifications with upstream seed updates.

Design principles:
- Lenient parsing: users may have manually edited files
- Safe degradation: if parsing fails, return original content or empty
- Preserve user data: drive values, "Our Story" sections, and skills are kept
"""

from __future__ import annotations

import re
from enum import Enum
from typing import Optional


class MergeStrategy(Enum):
    """Strategies for merging files during seed updates."""

    OVERWRITE = "overwrite"  # Complete overwrite
    PRESERVE = "preserve"  # Keep local unchanged
    SMART_MERGE = "smart_merge"  # Smart merge (e.g., SOUL.md)
    SECTION_MERGE = "section_merge"  # Section-based merge (e.g., STORY.md)
    UNION_MERGE = "union_merge"  # Union merge (e.g., AGENTS.md)


# === Drive Value Extraction ===

# Pattern to match drive headings like "### Curiosity (0.85)" with varying whitespace
# Also matches negative numbers and numbers > 1 for clamping
_DRIVE_PATTERN = re.compile(
    r"###\s*([A-Za-z_][A-Za-z0-9_\s]*?)\s*\(\s*(-?[0-9.]+)\s*\)", re.MULTILINE
)


def extract_drive_values(soul_md: Optional[str]) -> dict[str, float]:
    """Extract drive values from SOUL.md content.

    Args:
        soul_md: The SOUL.md content string, or None

    Returns:
        Dictionary mapping drive names to their values (0.0-1.0).
        Returns empty dict if content is None, empty, or has no drives.

    Examples:
        >>> extract_drive_values("### Curiosity (0.85)")
        {'Curiosity': 0.85}
    """
    if not soul_md:
        return {}

    values: dict[str, float] = {}

    for match in _DRIVE_PATTERN.finditer(soul_md):
        drive_name = match.group(1).strip()
        try:
            value = float(match.group(2))
            # Clamp to valid range
            value = max(0.0, min(1.0, value))
            values[drive_name] = value
        except ValueError:
            # Skip entries with invalid float values
            continue

    return values


def apply_drive_values(soul_md: Optional[str], values: dict[str, float]) -> str:
    """Apply drive values to SOUL.md content.

    Args:
        soul_md: The SOUL.md content string, or None
        values: Dictionary of drive names to new values

    Returns:
        Modified SOUL.md content with updated drive values.
        Returns empty string if content is None.
        Returns original content if values is empty.

    Examples:
        >>> apply_drive_values("### Curiosity (0.5)", {"Curiosity": 0.9})
        '### Curiosity (0.9)'
    """
    if soul_md is None:
        return ""

    if not values:
        return soul_md

    result = soul_md

    for drive_name, new_value in values.items():
        # Pattern to match this specific drive
        pattern = re.compile(
            rf"(###\s*){re.escape(drive_name)}(\s*)\(\s*[0-9.]+\s*\)", re.MULTILINE
        )
        # Replace with new value, preserving whitespace style
        result = pattern.sub(rf"\g<1>{drive_name}\g<2>({new_value})", result)

    return result


# === SOUL.md Merge ===


def merge_soul_md(local: Optional[str], upstream: Optional[str]) -> str:
    """Merge SOUL.md files, preserving local drive values.

    Strategy:
    - Use upstream as the base (for updated descriptions, new sections)
    - Preserve local drive values (user's evolved personality)
    - Add new drives from upstream with their default values
    - Remove drives that no longer exist in upstream

    Args:
        local: The local (user-modified) SOUL.md content
        upstream: The upstream (seed update) SOUL.md content

    Returns:
        Merged SOUL.md content.

    Examples:
        >>> local = "### Curiosity (0.9)\\nDesc."
        >>> upstream = "### Curiosity (0.5)\\nNew desc."
        >>> merge_soul_md(local, upstream)
        '### Curiosity (0.9)\\nNew desc.'
    """
    if not upstream:
        return local or ""
    if not local:
        return upstream

    # Extract local drive values (the user's evolved personality)
    local_values = extract_drive_values(local)

    # Use upstream as base and apply local values
    return apply_drive_values(upstream, local_values)


# === Our Story Extraction ===

# Pattern to match "## Our Story" section until next ## or end
_OUR_STORY_PATTERN = re.compile(
    r"(## Our Story\b.*?)(?=\n## |\Z)", re.DOTALL | re.MULTILINE
)


def extract_our_story_section(story_md: Optional[str]) -> Optional[str]:
    """Extract the "Our Story" section from STORY.md.

    Args:
        story_md: The STORY.md content string, or None

    Returns:
        The "Our Story" section including the heading, or None if not found.

    Examples:
        >>> extract_our_story_section("## Our Story\\n\\nContent here.")
        '## Our Story\\n\\nContent here.'
    """
    if not story_md:
        return None

    match = _OUR_STORY_PATTERN.search(story_md)
    if match:
        return match.group(1).rstrip()

    return None


# === Skills Extraction ===

# Pattern to match skill items in backticks like "- `fs.read`"
_SKILL_PATTERN = re.compile(r"-\s*`([^`]+)`")


def extract_skills(agents_md: Optional[str]) -> set[str]:
    """Extract skill names from AGENTS.md content.

    Args:
        agents_md: The AGENTS.md content string, or None

    Returns:
        Set of skill names found in backticks.

    Examples:
        >>> extract_skills("- `fs.read`\\n- `fs.write`")
        {'fs.read', 'fs.write'}
    """
    if not agents_md:
        return set()

    skills: set[str] = set()

    for match in _SKILL_PATTERN.finditer(agents_md):
        skills.add(match.group(1))

    return skills


# === AGENTS.md Merge ===


def merge_agents_md(local: Optional[str], upstream: Optional[str]) -> str:
    """Merge AGENTS.md files using union of skills.

    Strategy:
    - Combine skills from both local and upstream (union)
    - Use upstream structure for the output
    - Remove duplicates
    - Remove 'read_only' placeholder if real skills exist

    Args:
        local: The local (user-modified) AGENTS.md content
        upstream: The upstream (seed update) AGENTS.md content

    Returns:
        Merged AGENTS.md content with all unique skills.

    Examples:
        >>> local = "- `fs.read`"
        >>> upstream = "- `shell.exec`"
        >>> merge_agents_md(local, upstream)  # Contains both skills
    """
    if not upstream:
        return local or ""
    if not local:
        return upstream

    # Extract skills from both
    local_skills = extract_skills(local)
    upstream_skills = extract_skills(upstream)

    # Union of all skills
    all_skills = local_skills | upstream_skills

    # Remove 'read_only' if there are real skills
    if len(all_skills) > 1 and "read_only" in all_skills:
        all_skills.discard("read_only")

    # Build output using upstream structure
    lines: list[str] = []

    # Find the header and any intro text from upstream
    in_header = True
    for line in upstream.split("\n"):
        if line.startswith("- `"):
            in_header = False
            break
        lines.append(line)

    # Add all skills (sorted for consistency)
    for skill in sorted(all_skills):
        lines.append(f"- `{skill}`")

    # Add any trailing content from upstream (like notes)
    found_skills_section = False
    after_skills_content: list[str] = []

    for line in upstream.split("\n"):
        if line.startswith("- `"):
            found_skills_section = True
        elif found_skills_section and line.strip() and not line.startswith("-"):
            after_skills_content.append(line)

    if after_skills_content:
        lines.append("")
        lines.extend(after_skills_content)
    else:
        lines.append("")

    return "\n".join(lines)


# === STORY.md Merge ===


def merge_story_md(local: Optional[str], upstream: Optional[str]) -> str:
    """Merge STORY.md files, preserving local "Our Story" section.

    Strategy:
    - Use upstream content as base (for updated sections)
    - Preserve local "Our Story" section if it exists
    - If no local "Our Story", use upstream's version

    Args:
        local: The local (user-modified) STORY.md content
        upstream: The upstream (seed update) STORY.md content

    Returns:
        Merged STORY.md content.

    Examples:
        >>> local = "## Our Story\\n\\nLocal story."
        >>> upstream = "## Who I Am\\n\\nBio.\\n## Our Story\\n\\nUpstream."
        >>> merge_story_md(local, upstream)  # Contains local story
    """
    if not upstream:
        return local or ""
    if not local:
        return upstream

    # Extract local "Our Story" section
    local_our_story = extract_our_story_section(local)

    if not local_our_story:
        # No local "Our Story" to preserve, use upstream as-is
        return upstream

    # Replace upstream's "Our Story" with local version
    upstream_our_story = extract_our_story_section(upstream)

    if upstream_our_story:
        # Replace upstream section with local section
        return upstream.replace(upstream_our_story, local_our_story)
    else:
        # No "Our Story" in upstream, append local version
        return upstream.rstrip() + "\n\n" + local_our_story + "\n"
