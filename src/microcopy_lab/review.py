"""Explicit, version-specific human decisions without modifying source records."""

import hashlib
import json
from collections import Counter
from typing import Literal

from pydantic import Field

from microcopy_lab.config import StyleGuide
from microcopy_lab.models import Project, ProposedRevision, Record, ReviewStatus, UIString
from microcopy_lab.placeholders import validate_placeholder_integrity
from microcopy_lab.terminology import phrase_matches


class ReviewEntry(Record):
    """A revision and the exact source/configuration against which it was reviewed."""

    revision: ProposedRevision
    initial_revision: ProposedRevision | None = None
    edited_by_human: bool = False
    source: UIString
    source_fingerprint: str
    origin: Literal["manual", "ai_assisted", "illustrative"]
    version: int = Field(default=1, ge=1)
    notes: str = Field(default="", max_length=10000)
    behavior_confirmed: bool = False


def source_fingerprint(project: Project, source: UIString, guide: StyleGuide) -> str:
    """Bind decisions to source metadata, product context, project, and full style guide."""
    data = [
        project.project_id,
        project.product_context,
        source.model_dump(mode="json"),
        guide.model_dump(mode="json"),
    ]
    return hashlib.sha256(json.dumps(data, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def is_current(entry: ReviewEntry, project: Project, guide: StyleGuide) -> bool:
    """Exclude decisions made against different source/configuration data."""
    source = next((s for s in project.strings if s.string_id == entry.revision.string_id), None)
    return (
        source is not None
        and entry.source.model_dump(mode="json") == source.model_dump(mode="json")
        and entry.source_fingerprint == source_fingerprint(project, source, guide)
    )


def create_entry(
    project: Project,
    guide: StyleGuide,
    revision: ProposedRevision,
    *,
    origin: Literal["manual", "ai_assisted", "illustrative"],
) -> ReviewEntry:
    """Import a candidate as pending, ignoring any supplied approval or token claim."""
    source = next((s for s in project.strings if s.string_id == revision.string_id), None)
    if source is None:
        raise ValueError("The revision must reference a current catalog string.")
    candidate = ProposedRevision.model_validate_json(revision.model_dump_json())
    candidate.review_status = ReviewStatus.PENDING
    candidate.protected_tokens_valid = validate_placeholder_integrity(
        source, candidate.suggested_text, syntaxes=guide.placeholder_syntaxes
    ).valid
    return ReviewEntry(
        revision=candidate,
        initial_revision=candidate.model_copy(deep=True),
        source=source.model_copy(deep=True),
        source_fingerprint=source_fingerprint(project, source, guide),
        origin=origin,
    )


def approval_problems(entry: ReviewEntry, project: Project, guide: StyleGuide) -> list[str]:
    """Recheck mechanical safety; product meaning remains a human responsibility."""
    problems = []
    if not is_current(entry, project, guide):
        problems.append(
            "Source, product context, or style guide changed. Rebase this draft before review."
        )
    text = entry.revision.suggested_text
    if not text.strip():
        problems.append("Replacement text must be nonblank.")
    if not validate_placeholder_integrity(
        entry.source, text, syntaxes=guide.placeholder_syntaxes
    ).valid:
        problems.append("Replacement text must preserve the exact protected tokens and counts.")
    limit = entry.source.max_chars or guide.limit_for(entry.source.component_type)
    if len(text) > limit:
        problems.append("Replacement text exceeds its character limit.")
    if any(
        Counter(m.text for m in phrase_matches(entry.source.original_text, term))
        != Counter(m.text for m in phrase_matches(text, term))
        for term in guide.protected_terms
    ):
        problems.append("Replacement text must preserve protected product terms.")
    if not entry.behavior_confirmed:
        problems.append("Confirm that the replacement preserves verified product behavior.")
    return problems


def update_entry(
    entry: ReviewEntry,
    project: Project,
    guide: StyleGuide,
    *,
    text: str,
    rationale: str,
    notes: str,
    status: ReviewStatus,
    behavior_confirmed: bool,
    others: list[ReviewEntry],
) -> ReviewEntry:
    """Edit a copy atomically; material edits reset decisions even if Approve was selected."""
    updated = ReviewEntry.model_validate_json(entry.model_dump_json())
    material = text != entry.revision.suggested_text or rationale != entry.revision.rationale
    if not text.strip() or not rationale.strip():
        raise ValueError("Replacement text and rationale must be nonblank.")
    candidate_data = updated.revision.model_dump(mode="json")
    candidate_data.update(suggested_text=text, rationale=rationale)
    updated.revision = ProposedRevision.model_validate_json(json.dumps(candidate_data))
    updated.notes = notes
    updated.behavior_confirmed = behavior_confirmed
    if material:
        updated.version += 1
        updated.edited_by_human = True
        updated.behavior_confirmed = False
        updated.revision.evidence_quote = None
        updated.revision.review_status = ReviewStatus.PENDING
    else:
        updated.revision.review_status = ReviewStatus(status)
    updated = ReviewEntry.model_validate_json(updated.model_dump_json())
    updated.revision.protected_tokens_valid = validate_placeholder_integrity(
        updated.source, text, syntaxes=guide.placeholder_syntaxes
    ).valid
    if updated.revision.review_status == ReviewStatus.APPROVED:
        problems = approval_problems(updated, project, guide)
        if any(
            other.revision.revision_id != updated.revision.revision_id
            and other.revision.string_id == updated.revision.string_id
            and other.revision.review_status == ReviewStatus.APPROVED
            and is_current(other, project, guide)
            for other in others
        ):
            problems.append(
                "Another revision for this string is approved. Change its status first."
            )
        if problems:
            raise ValueError(" ".join(problems))
    return updated


def rebase_entry(entry: ReviewEntry, project: Project, guide: StyleGuide) -> ReviewEntry:
    """Explicitly attach a retained draft to current source data, resetting its decision."""
    updated = create_entry(project, guide, entry.revision, origin=entry.origin)
    updated.version = entry.version + 1
    updated.notes = entry.notes
    updated.initial_revision = entry.initial_revision
    updated.edited_by_human = entry.edited_by_human
    return updated
