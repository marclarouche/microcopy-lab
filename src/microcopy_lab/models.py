"""Versioned domain records; source content is always data."""

from enum import StrEnum
from typing import Annotated, Literal
from uuid import uuid4

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    field_validator,
    model_validator,
)

Identifier = Annotated[
    str, StringConstraints(min_length=1, max_length=200, pattern=r"^[^\s\x00-\x1f\x7f]+$")
]
Nonempty = Annotated[str, StringConstraints(min_length=1, max_length=100_000)]


def new_id() -> str:
    """Create an identifier once, retained when the record is serialized."""
    return str(uuid4())


class Record(BaseModel):
    """Common schema version and lossless extension fields."""

    model_config = ConfigDict(extra="allow", strict=True)
    schema_version: Literal["1.0"] = "1.0"


class ComponentType(StrEnum):
    """Supported component categories."""

    BUTTON = "button"
    FIELD_LABEL = "field_label"
    TOOLTIP = "tooltip"
    ERROR_WARNING = "error_warning"
    ONBOARDING_EMPTY_STATE = "onboarding_empty_state"


class ReviewStatus(StrEnum):
    """Explicit human editorial decisions for a revision version."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_CLARIFICATION = "needs_clarification"


class UIString(Record):
    """Original string and its source context, without editorial changes."""

    string_id: Identifier
    component_type: ComponentType
    original_text: Nonempty
    context: Nonempty
    screen_id: str | None = None
    product_area: str | None = None
    user_goal: str | None = None
    max_chars: int | None = Field(default=None, gt=0, le=100_000)
    product_behavior: str | None = None
    design_notes: str | None = None
    protected_tokens: list[Annotated[str, StringConstraints(min_length=1, max_length=200)]] = Field(
        default_factory=list, max_length=1000
    )
    source_reference: str | None = None

    @field_validator("protected_tokens")
    @classmethod
    def valid_tokens(cls, tokens: list[str]) -> list[str]:
        """Require nonblank literal declarations without changing their spelling."""
        if any(not token.strip() for token in tokens):
            raise ValueError("Protected token declarations must be nonblank")
        return tokens

    @field_validator("component_type", mode="before")
    @classmethod
    def component(cls, value: object) -> ComponentType:
        """Accept component names in Python mappings as well as JSON."""
        if not isinstance(value, str):
            raise ValueError("Unsupported component type")  # noqa: TRY004 — validators need ValueError
        return ComponentType(value)

    @field_validator("original_text", "context")
    @classmethod
    def nonblank(cls, value: str) -> str:
        """Reject blank values without stripping source whitespace."""
        if not value.strip():
            raise ValueError("A nonblank value is required")
        return value


class ValidationWarning(Record):
    """Safe diagnostic without source text or parser internals."""

    warning_id: str = Field(default_factory=new_id)
    code: str
    message: str
    row: int | None = None
    string_id: str | None = None
    severity: Literal["error", "warning"] = "error"


class ImportResult(Record):
    """Accepted records and diagnostics; fatal input errors accept nothing."""

    strings: list[UIString] = Field(default_factory=list)
    warnings: list[ValidationWarning] = Field(default_factory=list)
    rejected_count: int = 0
    fatal: bool = False


class Project(Record):
    """In-memory project boundary with unique source identifiers."""

    project_id: Identifier = Field(default_factory=new_id)
    name: Nonempty
    product_context: str = ""
    strings: list[UIString] = Field(default_factory=list)

    @model_validator(mode="after")
    def unique_ids(self) -> "Project":
        """Prevent ambiguous source references."""
        ids = [item.string_id for item in self.strings]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate string identifiers")
        return self


class AuditFinding(Record):
    """Source-linked advisory finding, separate from original content."""

    finding_id: Identifier = Field(default_factory=new_id)
    string_id: Identifier
    category: str
    severity: Literal["low", "medium", "high"]
    detection_method: Literal["deterministic", "ai_assisted"]
    explanation: Nonempty
    rule_id: str | None = None
    review_status: ReviewStatus = ReviewStatus.PENDING
    matched_text: str | None = None
    start: int | None = Field(default=None, ge=0)
    end: int | None = Field(default=None, ge=0)
    related_string_ids: list[str] = Field(default_factory=list)
    requires_behavior_confirmation: bool = False


class ProposedRevision(Record):
    """Pending source-linked candidate; never an automatically accepted replacement."""

    revision_id: Identifier = Field(default_factory=new_id)
    string_id: Identifier
    finding_id: str | None = None
    suggested_text: Nonempty
    rationale: Nonempty
    requires_behavior_confirmation: bool = True
    protected_tokens_valid: bool = False
    review_status: ReviewStatus = ReviewStatus.PENDING
    category: str | None = None
    severity: Literal["low", "medium", "high"] | None = None
    rule_id: str | None = None
    model_identifier: str | None = None
    evidence_quote: str | None = None


class TokenValidation(Record):
    """Multiset comparison of protected source and candidate tokens."""

    valid: bool
    missing: dict[str, int] = Field(default_factory=dict)
    added: dict[str, int] = Field(default_factory=dict)
    source_tokens: dict[str, int] = Field(default_factory=dict)
    candidate_tokens: dict[str, int] = Field(default_factory=dict)
    absent_declared_tokens: list[str] = Field(default_factory=list)


class AuditSummary(Record):
    """Counts only; no aggregate quality score or compliance assessment."""

    total_strings: int
    strings_analyzed: int
    strings_with_findings: int
    findings_by_category: dict[str, int]
    findings_by_severity: dict[str, int]
    character_limit_violations: int


class AuditResult(Record):
    """Reproducible in-memory deterministic audit and its input fingerprint."""

    project_id: Identifier
    style_guide_name: str
    style_guide_version: str
    engine_version: str
    input_fingerprint: str
    findings: list[AuditFinding]
    summary: AuditSummary
