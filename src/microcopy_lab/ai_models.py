"""Strict, bounded contracts at the model trust boundary."""

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from microcopy_lab.models import AuditFinding, ProposedRevision, Record

Text = Annotated[str, StringConstraints(min_length=1, max_length=2000, strip_whitespace=True)]
AI_CATEGORY = Literal[
    "clarity",
    "terminology",
    "tone",
    "actionability",
    "accessibility_wording",
    "jargon",
    "error_recovery",
    "instructions",
]


class ModelFinding(BaseModel):
    """Untrusted model output; identifiers and review states are app-owned."""

    model_config = ConfigDict(extra="forbid", strict=True)
    category: AI_CATEGORY
    severity: Literal["low", "medium", "high"]
    explanation: Text
    suggested_text: Annotated[str, StringConstraints(min_length=1, max_length=2000)] | None
    rationale: Text | None
    evidence_quote: Text | None
    clarification_question: Text | None


class ModelResponse(BaseModel):
    """Exactly one requested source per bounded local inference request."""

    model_config = ConfigDict(extra="forbid", strict=True)
    string_id: Annotated[str, StringConstraints(min_length=1, max_length=200)]
    findings: list[ModelFinding] = Field(max_length=5)


class LocalModel(BaseModel):
    """Locally installed model identity from the daemon."""

    name: str
    digest: str
    size: int


class AIDiagnostic(Record):
    """Safe user-facing failure with no raw model output or source contents."""

    code: str
    message: str


class Clarification(Record):
    """A question instead of an unsupported product assertion."""

    string_id: str
    finding_id: str | None = None
    question: str


class AIRecordResult(Record):
    """Independent record outcome, including partial/rejected output."""

    string_id: str
    status: Literal["completed", "needs_clarification", "partial", "failed"]
    findings: list[AuditFinding] = Field(default_factory=list)
    revisions: list[ProposedRevision] = Field(default_factory=list)
    clarifications: list[Clarification] = Field(default_factory=list)
    diagnostics: list[AIDiagnostic] = Field(default_factory=list)


class AIAnalysisResult(Record):
    """AI run traceability and per-source outcomes; never overwrites source."""

    project_id: str
    model_identifier: str
    model_digest: str | None
    style_guide_version: str
    application_version: str
    prompt_version: str
    source_fingerprint: str = ""
    input_fingerprint: str
    requested_ids: list[str]
    records: list[AIRecordResult]
    status: Literal["completed", "partial", "failed"]
    analyzed_count: int
    failed_count: int
    partial_count: int
    clarification_count: int
