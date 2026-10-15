"""UI-independent preview snapshots, literal content, and approximate fit metrics."""

import json
import math
import unicodedata
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, model_validator

from microcopy_lab.config import StyleGuide
from microcopy_lab.models import ComponentType, ProposedRevision, TokenValidation, UIString
from microcopy_lab.placeholders import token_spans, validate_placeholder_integrity

PREVIEW_VERSION = "preview-1.0"


class LayoutSize(StrEnum):
    """Predefined illustrative frame widths, not production breakpoints."""

    COMPACT = "compact"
    COMFORTABLE = "comfortable"
    WIDE = "wide"


class PreviewTheme(StrEnum):
    """Presentation palettes; source content never supplies style instructions."""

    LIGHT = "light"
    DARK = "dark"


FRAME_WIDTHS: dict[LayoutSize, int] = {
    LayoutSize.COMPACT: 260,
    LayoutSize.COMFORTABLE: 360,
    LayoutSize.WIDE: 520,
}
CONTENT_PADDING: dict[ComponentType, int] = {
    ComponentType.BUTTON: 68,
    ComponentType.FIELD_LABEL: 50,
    ComponentType.TOOLTIP: 73,
    ComponentType.ERROR_WARNING: 82,
    ComponentType.ONBOARDING_EMPTY_STATE: 58,
}
VISIBLE_LINES: dict[ComponentType, int] = {
    ComponentType.BUTTON: 1,
    ComponentType.FIELD_LABEL: 2,
    ComponentType.TOOLTIP: 4,
    ComponentType.ERROR_WARNING: 4,
    ComponentType.ONBOARDING_EMPTY_STATE: 6,
}


class PreviewVariant(BaseModel):
    """Exact copy and advisory metrics for one version of a component."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)
    version: Literal["original", "revised"]
    text: str
    character_count: int
    max_chars: int
    exceeds_character_limit: bool
    estimated_lines: int
    visible_lines: int
    may_overflow_layout: bool
    tokens: dict[str, int]


class PreviewComparison(BaseModel):
    """Source-linked snapshot, independent of rendering or application state."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)
    schema_version: Literal["1.0"] = "1.0"
    preview_version: str = PREVIEW_VERSION
    string_id: str
    component_type: ComponentType
    layout: LayoutSize
    frame_width_px: int
    original: PreviewVariant
    revised: PreviewVariant | None
    revision_id: str | None
    token_validation: TokenValidation | None
    revision_blocked_reason: str | None


class PreviewExample(BaseModel):
    """Human-authored illustrative pair; never represented as AI output/approval."""

    model_config = ConfigDict(extra="forbid", strict=True)
    schema_version: Literal["1.0"] = "1.0"
    example_id: str
    description: str = Field(max_length=500)
    source: UIString
    revision: ProposedRevision

    @model_validator(mode="after")
    def linked_source(self) -> "PreviewExample":
        """Require a source-linked pending, explicitly illustrative revision."""
        if self.source.string_id != self.revision.string_id:
            raise ValueError("Preview example source link does not match")
        if (
            self.revision.model_identifier is not None
            or self.revision.review_status.value != "pending"
            or not self.revision.requires_behavior_confirmation
        ):
            raise ValueError("Illustrative previews cannot claim AI provenance or approval")
        return self


def estimate_lines(text: str, columns: int) -> int:
    """Conservative display-cell estimate, not browser/font measurement.

    Explicit newlines count; combining/format marks do not add cells. Wide
    characters count as two. Emoji sequences can be overestimated. Tabs use
    four-column stops. The original string is never normalized or replaced.
    """
    if columns < 1:
        raise ValueError("Layout columns must be positive")
    lines = 0
    for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        cells = 0
        for character in line:
            if character == "\t":
                cells += 4 - cells % 4
            elif unicodedata.combining(character) or unicodedata.category(character) in {
                "Cf",
                "Mn",
                "Me",
            }:
                continue
            else:
                cells += 2 if unicodedata.east_asian_width(character) in {"W", "F"} else 1
        lines += max(1, math.ceil(cells / columns))
    return lines


def _variant(
    source: UIString,
    text: str,
    version: Literal["original", "revised"],
    guide: StyleGuide,
    layout: LayoutSize,
) -> PreviewVariant:
    limit = (
        source.max_chars if source.max_chars is not None else guide.limit_for(source.component_type)
    )
    # Approximate 7 px per display cell after template frame/control padding.
    columns = max(1, (FRAME_WIDTHS[layout] - CONTENT_PADDING[source.component_type]) // 7)
    lines = estimate_lines(text, columns)
    visible = VISIBLE_LINES[source.component_type]
    tokens: dict[str, int] = {}
    for span in token_spans(text, source.protected_tokens, syntaxes=guide.placeholder_syntaxes):
        tokens[span.token] = tokens.get(span.token, 0) + 1
    return PreviewVariant(
        version=version,
        text=text,
        character_count=len(text),
        max_chars=limit,
        exceeds_character_limit=len(text) > limit,
        estimated_lines=lines,
        visible_lines=visible,
        may_overflow_layout=lines > visible,
        tokens=dict(sorted(tokens.items())),
    )


def build_preview(
    source: UIString,
    guide: StyleGuide,
    revision: ProposedRevision | None = None,
    *,
    layout: LayoutSize = LayoutSize.COMFORTABLE,
) -> PreviewComparison:
    """Build exact original/revised snapshots; recheck tokens rather than trust flags.

    Length/fit violations remain visible for comparison. Foreign-source or
    token-invalid candidates are withheld. This is no editorial acceptance path.
    Callers must provide only revisions current for their source/configuration.
    """
    original = _variant(source, source.original_text, "original", guide, layout)
    revised = None
    integrity = None
    blocked = None
    if revision is not None:
        if revision.string_id != source.string_id:
            blocked = "The candidate belongs to a different source string."
        else:
            integrity = validate_placeholder_integrity(
                source, revision.suggested_text, syntaxes=guide.placeholder_syntaxes
            )
            if not integrity.valid:
                blocked = (
                    "The candidate changes protected tokens or has inconsistent token metadata."
                )
            elif not revision.suggested_text.strip():
                blocked = "The candidate is blank."
            else:
                revised = _variant(source, revision.suggested_text, "revised", guide, layout)
    # Streamlit can retain records from a previous module generation after a
    # source reload. Cross this boundary as schema-validated data, not Python
    # class identities. Strict enum/model validation remains enabled.
    return PreviewComparison.model_validate_json(
        json.dumps(
            {
                "string_id": source.string_id,
                "component_type": source.component_type.value,
                "layout": layout.value,
                "frame_width_px": FRAME_WIDTHS[layout],
                "original": original.model_dump(mode="json"),
                "revised": revised.model_dump(mode="json") if revised else None,
                "revision_id": revision.revision_id if revision else None,
                "token_validation": integrity.model_dump(mode="json") if integrity else None,
                "revision_blocked_reason": blocked,
            }
        )
    )


def parse_preview_examples(data: bytes, guide: StyleGuide) -> list[PreviewExample]:
    """Validate a bounded local sample fixture, including IDs and token integrity."""
    if len(data) > 131_072:
        raise ValueError("Preview examples exceed the size limit")
    adapter: TypeAdapter[list[PreviewExample]] = TypeAdapter(list[PreviewExample])
    examples = adapter.validate_json(data)
    if len(examples) > 20:
        raise ValueError("Preview examples exceed the record limit")
    for identifiers in (
        [example.example_id for example in examples],
        [example.source.string_id for example in examples],
        [example.revision.revision_id for example in examples],
    ):
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("Preview examples contain duplicate identifiers")
    if any(
        build_preview(example.source, guide, example.revision).revision_blocked_reason
        for example in examples
    ):
        raise ValueError("Preview examples contain invalid token/source links")
    return examples
