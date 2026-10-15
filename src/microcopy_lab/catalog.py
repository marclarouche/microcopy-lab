"""Explicit validated source editing, separate from editorial replacement decisions."""

import json

from microcopy_lab.config import StyleGuide
from microcopy_lab.models import Project, UIString

EDITABLE_FIELDS = frozenset(
    {
        "component_type",
        "original_text",
        "context",
        "screen_id",
        "product_area",
        "user_goal",
        "max_chars",
        "product_behavior",
        "design_notes",
        "protected_tokens",
        "source_reference",
    }
)


def edit_source(
    project: Project, guide: StyleGuide, identifier: str, changes: dict[str, object]
) -> Project:
    """Return a validated copy; retain IDs, unknown metadata, and unrelated records.

    Source edits deliberately do not rebase review entries or reuse old analysis.
    The caller retains those drafts; their source fingerprints make them stale.
    """
    if set(changes) - EDITABLE_FIELDS:
        raise ValueError("Only supported source fields can be edited; identifiers stay unchanged.")
    if len(project.strings) > guide.max_records:
        raise ValueError("Project exceeds the configured record limit.")
    source = next((s for s in project.strings if s.string_id == identifier), None)
    if source is None:
        raise ValueError("Select a current catalog source.")
    data = source.model_dump(mode="json")
    data.update(changes)
    updated = UIString.model_validate_json(json.dumps(data))
    result = Project.model_validate_json(project.model_dump_json())
    result.strings = [updated if s.string_id == identifier else s for s in result.strings]
    return result
