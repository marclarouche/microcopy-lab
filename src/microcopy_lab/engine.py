"""Independent deterministic audit orchestration and reproducible findings."""

import hashlib
import json
from collections import Counter, defaultdict
from uuid import NAMESPACE_URL, uuid5

from microcopy_lab import __version__
from microcopy_lab.config import StyleGuide
from microcopy_lab.models import AuditFinding, AuditResult, AuditSummary, Project, UIString
from microcopy_lab.rules import RuleMatch, check_string
from microcopy_lab.terminology import canonical_text, phrase_matches, protected_spans

ENGINE_VERSION = "deterministic-1.0"


def audit_fingerprint(project: Project, guide: StyleGuide) -> str:
    """Fingerprint all source/configuration data to invalidate stale UI results."""
    payload = {
        "project": project.model_dump(mode="json"),
        "guide": guide.model_dump(mode="json"),
        "engine": ENGINE_VERSION,
        "application": __version__,
    }
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()
    ).hexdigest()


def _finding(
    project: Project, item: UIString, match: RuleMatch, related: list[str] | None = None
) -> AuditFinding:
    evidence = {
        "project": project.project_id,
        "source": item.string_id,
        "text": item.original_text,
        "rule": match.rule_id,
        "start": match.start,
        "end": match.end,
        "match": match.matched_text,
        "explanation": match.explanation,
        "related": related or [],
        "engine": ENGINE_VERSION,
    }
    identifier = str(uuid5(NAMESPACE_URL, json.dumps(evidence, sort_keys=True, ensure_ascii=False)))
    return AuditFinding(
        finding_id=identifier,
        string_id=item.string_id,
        category=match.category,
        severity=match.severity,
        detection_method="deterministic",
        explanation=match.explanation,
        rule_id=match.rule_id,
        matched_text=match.matched_text,
        start=match.start,
        end=match.end,
        related_string_ids=related or [],
        requires_behavior_confirmation=match.requires_behavior_confirmation,
    )


def audit_project(project: Project, guide: StyleGuide) -> AuditResult:
    """Audit every validated string, preserving inputs and stable source references.

    Repeated equivalent runs have identical ordered findings and IDs. The engine
    has no IO, model client, Streamlit dependency, or automatic replacement path.
    """
    if len(project.strings) > guide.max_records:
        raise ValueError("Project exceeds the configured record limit")
    if len({item.string_id for item in project.strings}) != len(project.strings):
        raise ValueError("Project contains duplicate identifiers")
    findings = [
        _finding(project, item, match)
        for item in sorted(project.strings, key=lambda item: item.string_id)
        for match in check_string(item, guide)
    ]
    if guide.enabled("consistency"):
        groups: dict[tuple[str | None, str, str], list[UIString]] = defaultdict(list)
        for item in project.strings:
            groups[(item.screen_id, item.component_type.value, canonical_text(item, guide))].append(
                item
            )
        for members in groups.values():
            variants = {" ".join(item.original_text.split()).casefold() for item in members}
            if len(variants) < 2:
                continue
            has_discouraged = any(
                phrase_matches(item.original_text, term, protected_spans(item, guide))
                for item in members
                for term in guide.terminology
            )
            if len(variants) > 1 and has_discouraged:
                for item in members:
                    related = sorted(
                        other.string_id for other in members if other.string_id != item.string_id
                    )
                    findings.append(
                        _finding(
                            project,
                            item,
                            RuleMatch(
                                "CATALOG-TERM-VARIANTS",
                                "consistency",
                                "medium",
                                "Related strings on this screen differ only by configured terminology. Confirm whether they identify the same action or concept.",
                                requires_behavior_confirmation=True,
                            ),
                            related,
                        )
                    )
    findings.sort(
        key=lambda finding: (
            finding.string_id,
            finding.rule_id or "",
            finding.start if finding.start is not None else -1,
            finding.finding_id,
        )
    )
    categories = dict(sorted(Counter(finding.category for finding in findings).items()))
    severities: dict[str, int] = {
        str(key): count
        for key, count in sorted(Counter(finding.severity for finding in findings).items())
    }
    summary = AuditSummary(
        total_strings=len(project.strings),
        strings_analyzed=len(project.strings),
        strings_with_findings=len({finding.string_id for finding in findings}),
        findings_by_category=categories,
        findings_by_severity=severities,
        character_limit_violations=categories.get("length", 0),
    )
    return AuditResult(
        project_id=project.project_id,
        style_guide_name=guide.name,
        style_guide_version=guide.version,
        engine_version=ENGINE_VERSION,
        input_fingerprint=audit_fingerprint(project, guide),
        findings=findings,
        summary=summary,
    )
