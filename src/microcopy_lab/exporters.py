"""In-memory, source-linked review reports; no filesystem or network access."""

import csv
import io
import json
import re
from collections import Counter
from datetime import UTC, datetime
from html import escape
from typing import Any

from microcopy_lab import __version__
from microcopy_lab.ai_models import AIAnalysisResult
from microcopy_lab.config import StyleGuide
from microcopy_lab.engine import audit_fingerprint, audit_project
from microcopy_lab.importers import validate_records
from microcopy_lab.models import Project, ReviewStatus
from microcopy_lab.placeholders import validate_placeholder_integrity
from microcopy_lab.review import ReviewEntry, approval_problems, is_current

LIMITATIONS = [
    "Human review is required; approval does not certify product behavior or accessibility.",
    "Previews estimate layout fit and do not verify production interfaces.",
    "AI output may be incomplete or incorrect; no source application is modified.",
    "Session data is held in memory. Download reports before ending the session.",
    "CSV formula-like cells are prefixed with an apostrophe for spreadsheet safety; JSON preserves exact text.",
    "Stale review decisions are reported as pending and excluded from approved replacements.",
]


def build_report(
    project: Project,
    guide: StyleGuide,
    entries: list[ReviewEntry],
    *,
    ai: AIAnalysisResult | None = None,
) -> dict[str, Any]:
    """Build a fresh deterministic audit and export only mechanically valid approvals.

    The caller must supply only the AI result currently matching its UI settings
    and selection. Review entries are independently rebound to source/context.
    """
    audit = audit_project(project, guide)
    identifiers = {s.string_id for s in project.strings}
    if len({e.revision.revision_id for e in entries}) != len(entries):
        raise ValueError("Revision identifiers must be unique.")
    if any(e.revision.string_id not in identifiers for e in entries):
        raise ValueError("All revisions must reference this catalog.")
    if ai is not None and (
        ai.source_fingerprint != audit_fingerprint(project, guide)
        or ai.project_id != project.project_id
        or any(record.string_id not in identifiers for record in ai.records)
    ):
        raise ValueError("AI results must belong to this project and catalog.")
    reviews = []
    approved = []
    for entry in entries:
        row = entry.model_dump(mode="json")
        row["stale"] = not is_current(entry, project, guide)
        blocked = approval_problems(entry, project, guide)
        row["approval_problems"] = blocked
        if row["stale"] or (entry.revision.review_status == ReviewStatus.APPROVED and blocked):
            row["revision"]["review_status"] = "pending"
            row["behavior_confirmed"] = False
        row["revision"]["protected_tokens_valid"] = validate_placeholder_integrity(
            entry.source, entry.revision.suggested_text, syntaxes=guide.placeholder_syntaxes
        ).valid
        reviews.append(row)
        if row["revision"]["review_status"] == "approved":
            approved.append(
                {
                    "string_id": entry.source.string_id,
                    "original_text": entry.source.original_text,
                    "replacement_text": entry.revision.suggested_text,
                    "revision_id": entry.revision.revision_id,
                    "revision_version": entry.version,
                }
            )
    if len({r["string_id"] for r in approved}) != len(approved):
        raise ValueError("Only one approved revision per source may be exported.")
    findings = [f.model_dump(mode="json") for f in audit.findings]
    if ai:
        findings.extend(f.model_dump(mode="json") for record in ai.records for f in record.findings)
    statuses = Counter(row["revision"]["review_status"] for row in reviews)
    summary = {
        "total_strings": len(project.strings),
        "strings_analyzed": len(project.strings),
        "analysis_methods": ["deterministic"] + (["ai_assisted"] if ai else []),
        "findings_by_category": dict(Counter(f["category"] for f in findings)),
        "findings_by_severity": dict(Counter(f["severity"] for f in findings)),
        "pending_review_count": statuses["pending"],
        "approved_revision_count": len(approved),
        "rejected_revision_count": statuses["rejected"],
        "needs_clarification_count": statuses["needs_clarification"],
        "stale_revision_count": sum(row["stale"] for row in reviews),
        "character_limit_violations": sum(
            w.code == "character_limit"
            for w in validate_records(
                [s.model_dump() for s in project.strings], guide=guide
            ).warnings
        ),
        "failed_analysis_count": ai.failed_count if ai else 0,
        "partial_analysis_count": ai.partial_count if ai else 0,
    }
    return {
        "schema_version": "1.0",
        "session_id": project.project_id,
        "application_version": __version__,
        "generated_at": datetime.now(UTC).isoformat(),
        "project": project.model_dump(mode="json"),
        "style_guide": guide.model_dump(mode="json"),
        "input_fingerprint": audit_fingerprint(project, guide),
        "summary": summary,
        "findings": findings,
        "reviews": reviews,
        "approved_replacements": approved,
        "ai_analysis": ai.model_dump(mode="json") if ai else None,
        "validation_warnings": [
            w.model_dump(mode="json")
            for w in validate_records(
                [s.model_dump() for s in project.strings], guide=guide
            ).warnings
        ],
        "limitations": LIMITATIONS,
    }


def export_json(report: dict[str, Any]) -> str:
    """Lossless UTF-8-compatible report with suggestions and approvals separated."""
    return json.dumps(report, ensure_ascii=False, indent=2) + "\n"


def _cell(value: object) -> str:
    text = "" if value is None else str(value)
    if re.match(r"^[\s\x00-\x1f\ufeff]*[=+\-@]", text) or text.startswith(("\t", "\r", "\n")):
        return "'" + text
    return text


def export_csv(report: dict[str, Any], *, approved_only: bool = False) -> str:
    """One row per source/revision, or approved replacements only; neutralize formulas."""
    fields = [
        "project_id",
        "application_version",
        "style_guide_version",
        "string_id",
        "component_type",
        "original_text",
        "proposed_revision",
        "approved_text",
        "revision_id",
        "revision_version",
        "review_status",
        "category",
        "severity",
        "explanation",
        "rule_id",
        "finding_id",
        "finding_details",
        "model_identifier",
        "origin",
        "edited_by_human",
        "review_notes",
        "behavior_confirmed",
        "stale",
        "source_metadata",
        "limitations",
    ]
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields)
    writer.writeheader()
    for source in report["project"]["strings"]:
        reviews = [
            r for r in report["reviews"] if r["revision"]["string_id"] == source["string_id"]
        ]
        if approved_only:
            reviews = [r for r in reviews if r["revision"]["review_status"] == "approved"]
        for review in reviews or ([] if approved_only else [None]):
            revision = review["revision"] if review else {}
            status = revision.get("review_status", "unreviewed")
            row = {
                "project_id": report["project"]["project_id"],
                "application_version": report["application_version"],
                "style_guide_version": report["style_guide"]["version"],
                "string_id": source["string_id"],
                "component_type": source["component_type"],
                "original_text": source["original_text"],
                "proposed_revision": revision.get("suggested_text"),
                "approved_text": revision.get("suggested_text") if status == "approved" else None,
                "revision_id": revision.get("revision_id"),
                "revision_version": review["version"] if review else None,
                "review_status": status,
                "category": revision.get("category"),
                "severity": revision.get("severity"),
                "explanation": revision.get("rationale"),
                "rule_id": revision.get("rule_id"),
                "finding_id": revision.get("finding_id"),
                "finding_details": json.dumps(
                    [f for f in report["findings"] if f["string_id"] == source["string_id"]],
                    ensure_ascii=False,
                ),
                "model_identifier": revision.get("model_identifier"),
                "origin": review["origin"] if review else None,
                "edited_by_human": review["edited_by_human"] if review else None,
                "review_notes": review["notes"] if review else None,
                "behavior_confirmed": review["behavior_confirmed"] if review else None,
                "stale": review["stale"] if review else None,
                "source_metadata": json.dumps(source, ensure_ascii=False),
                "limitations": " ".join(report["limitations"]),
            }
            writer.writerow({key: _cell(value) for key, value in row.items()})
    return output.getvalue()


def _md(value: object) -> str:
    return re.sub(r"([\\`*_{}\[\]()#!|+\-.])", r"\\\1", escape(str(value))).replace("\n", "  \n")


def export_markdown(report: dict[str, Any]) -> str:
    """Escape imported markup/links; include every source, finding, and review decision."""
    lines = [
        "# Microcopy Lab editorial report",
        "",
        "Project: " + _md(report["project"]["name"]),
        "Project ID: " + _md(report["project"]["project_id"]),
        "Product context: " + _md(report["project"]["product_context"]),
        "Application: " + _md(report["application_version"]),
        "Style guide: "
        + _md(report["style_guide"]["name"])
        + " "
        + _md(report["style_guide"]["version"]),
        "Generated (UTC): " + _md(report["generated_at"]),
        "",
        "## Summary",
        "",
    ]
    lines.extend(f"- {_md(key)}: {_md(value)}" for key, value in report["summary"].items())
    for source in report["project"]["strings"]:
        lines.extend(
            [
                "",
                "## " + _md(source["string_id"]),
                "",
                "Original: " + _md(source["original_text"]),
                "Context: " + _md(source["context"]),
                "Metadata: " + _md(json.dumps(source, ensure_ascii=False)),
            ]
        )
        for finding in report["findings"]:
            if finding["string_id"] == source["string_id"]:
                lines.extend(["", "Finding: " + _md(json.dumps(finding, ensure_ascii=False))])
        for entry in report["reviews"]:
            if entry["revision"]["string_id"] == source["string_id"]:
                lines.extend(["", "Revision: " + _md(json.dumps(entry, ensure_ascii=False))])
    if report["ai_analysis"]:
        lines.extend(
            [
                "",
                "## Local AI processing",
                "",
                _md(json.dumps(report["ai_analysis"], ensure_ascii=False)),
            ]
        )
    lines.extend(["", "## Limitations", ""])
    lines.extend("- " + _md(item) for item in report["limitations"])
    return "\n".join(lines) + "\n"
