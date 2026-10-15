"""Configurable deterministic checks. Every match is advisory."""

import re
from dataclasses import dataclass
from typing import Literal

from microcopy_lab.config import Category, StyleGuide
from microcopy_lab.models import ComponentType, UIString
from microcopy_lab.terminology import phrase_matches, protected_spans


@dataclass(frozen=True)
class RuleMatch:
    """Intermediate rule evidence; the engine assigns stable finding IDs."""

    rule_id: str
    category: Category
    severity: Literal["low", "medium", "high"]
    explanation: str
    matched_text: str | None = None
    start: int | None = None
    end: int | None = None
    requires_behavior_confirmation: bool = False


def check_basic_text(
    text: str, component: ComponentType, limit: int, guide: StyleGuide
) -> list[RuleMatch]:
    """Check raw text including blanks rejected at the import boundary."""
    matches: list[RuleMatch] = []
    if guide.enabled("whitespace"):
        if not text.strip():
            matches.append(
                RuleMatch(
                    "TEXT-BLANK", "whitespace", "medium", "Provide a nonblank label or instruction."
                )
            )
        elif text != text.strip():
            matches.append(
                RuleMatch(
                    "TEXT-EDGE-WHITESPACE",
                    "whitespace",
                    "low",
                    "Review leading or trailing whitespace; preserve it if required by the product.",
                )
            )
    if guide.enabled("length") and len(text) > limit:
        matches.append(
            RuleMatch(
                "TEXT-LENGTH",
                "length",
                "medium",
                f"Text uses {len(text)} code points; the configured limit is {limit}.",
            )
        )
    if guide.enabled("punctuation"):
        for match in re.finditer(r"[!?]{2,}", text):
            matches.append(
                RuleMatch(
                    "TEXT-REPEATED-PUNCTUATION",
                    "punctuation",
                    "low",
                    "Review repeated exclamation or question marks.",
                    match[0],
                    match.start(),
                    match.end(),
                )
            )
    if guide.enabled("component"):
        if component != ComponentType.BUTTON or guide.writing_rules.get(
            "prefer_specific_actions", True
        ):
            component_rules = guide.component_rules.get(component)
            if component_rules and any(
                " ".join(text.split()).casefold() == " ".join(label.split()).casefold()
                for label in component_rules.discouraged_labels
            ):
                matches.append(
                    RuleMatch(
                        "COMPONENT-GENERIC-LABEL",
                        "component",
                        "medium",
                        "Configured generic wording: confirm the intended action or useful instruction before revising.",
                        requires_behavior_confirmation=True,
                    )
                )
        if (
            component == ComponentType.ERROR_WARNING
            and guide.writing_rules.get("avoid_unexplained_error_codes", True)
            and re.fullmatch(
                r"(?:error\s*)?(?:0x[0-9a-f]+|[a-z]+-?\d+|\d+)[.!]?", text.strip(), re.IGNORECASE
            )
        ):
            matches.append(
                RuleMatch(
                    "ERROR-CODE-ONLY",
                    "component",
                    "medium",
                    "This code-only message may need a plain-language explanation. Confirm cause and recovery with the product team.",
                    requires_behavior_confirmation=True,
                )
            )
    return matches


def check_string(item: UIString, guide: StyleGuide) -> list[RuleMatch]:
    """Run local rules without changing source text, metadata, or configuration."""
    limit = item.max_chars if item.max_chars is not None else guide.limit_for(item.component_type)
    spans = protected_spans(item, guide)
    matches = check_basic_text(item.original_text, item.component_type, limit, guide)
    # Punctuation inside protected tokens is technical data, not editorial copy.
    matches = [
        m
        for m in matches
        if m.start is None
        or m.end is None
        or not any(m.start < s.end and s.start < m.end for s in spans)
    ]
    if guide.enabled("terminology"):
        for term, preferred in sorted(guide.terminology.items()):
            for match in phrase_matches(item.original_text, term, spans):
                matches.append(
                    RuleMatch(
                        "TERM-PREFERRED",
                        "terminology",
                        "low",
                        f"Configured terminology prefers “{preferred}”. Verify that the product meaning remains correct.",
                        match.text,
                        match.start,
                        match.end,
                        True,
                    )
                )
    if guide.enabled("prohibited_phrase"):
        for phrase in sorted(set(guide.prohibited_phrases)):
            for match in phrase_matches(item.original_text, phrase, spans):
                matches.append(
                    RuleMatch(
                        "PHRASE-PROHIBITED",
                        "prohibited_phrase",
                        "medium",
                        "This phrase is prohibited by the active style guide; review it in product context.",
                        match.text,
                        match.start,
                        match.end,
                        True,
                    )
                )
    if guide.enabled("placeholders"):
        for token in sorted(set(item.protected_tokens)):
            if token not in item.original_text:
                matches.append(
                    RuleMatch(
                        "TOKEN-DECLARED-MISSING",
                        "placeholders",
                        "high",
                        "A declared protected token is absent from the original source. Confirm source metadata before editing.",
                        token,
                    )
                )
    return matches
