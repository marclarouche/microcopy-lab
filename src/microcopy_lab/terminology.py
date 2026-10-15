"""Unicode-aware literal phrase matching outside protected source spans."""

import json
import re
from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass

from microcopy_lab.config import StyleGuide
from microcopy_lab.models import UIString
from microcopy_lab.placeholders import TokenSpan, token_spans


@dataclass(frozen=True)
class PhraseMatch:
    """A source phrase and its original offsets."""

    text: str
    start: int
    end: int


def phrase_pattern(phrase: str) -> re.Pattern[str]:
    """Escape configuration literally, matching whole words and flexible spaces."""
    return re.compile(
        r"(?<!\w)" + r"\s+".join(re.escape(part) for part in phrase.split()) + r"(?!\w)",
        re.IGNORECASE,
    )


def phrase_matches(text: str, phrase: str, excluded: Sequence[TokenSpan] = ()) -> list[PhraseMatch]:
    """Return non-overlapping literal matches without changing the source."""
    return [
        PhraseMatch(match[0], match.start(), match.end())
        for match in phrase_pattern(phrase).finditer(text)
        if not any(match.start() < span.end and span.start < match.end() for span in excluded)
    ]


def protected_spans(item: UIString, guide: StyleGuide) -> list[TokenSpan]:
    """Protect placeholders and configured product/API terminology."""
    spans = token_spans(
        item.original_text, item.protected_tokens, syntaxes=guide.placeholder_syntaxes
    )
    for term in guide.protected_terms:
        spans.extend(
            TokenSpan(m.text, m.start, m.end) for m in phrase_matches(item.original_text, term)
        )
    return spans


def canonical_text(item: UIString, guide: StyleGuide) -> str:
    """Normalize terminology for advisory comparisons within a component/screen.

    Token spelling and case remain literal so distinct placeholder names cannot
    be grouped as equivalent. No original record is edited.
    """
    spans = protected_spans(item, guide)
    replacements: list[tuple[int, int, str]] = []
    for term, preferred in sorted(
        guide.terminology.items(), key=lambda pair: (-len(pair[0]), pair[0])
    ):
        for match in phrase_matches(item.original_text, term, spans):
            if not any(match.start < end and start < match.end for start, end, _ in replacements):
                replacements.append((match.start, match.end, preferred.casefold()))
    # Retain literal protected substrings and fold only ordinary copy.
    segments: list[tuple[int, int, str]] = replacements + [(s.start, s.end, s.token) for s in spans]
    output = []
    cursor = 0
    for start, end, value in sorted(segments, key=lambda entry: (entry[0], -entry[1])):
        if start < cursor:
            continue
        output.append(item.original_text[cursor:start].casefold())
        output.append(value)
        cursor = end
    output.append(item.original_text[cursor:].casefold())
    normalized = " ".join("".join(output).split())
    # Keep exact protected spelling/counts in the comparison key, including
    # whitespace inside literal custom tokens that ordinary copy normalization
    # would otherwise collapse.
    protected_counts = sorted(Counter(span.token for span in spans).items())
    return json.dumps([normalized, protected_counts], ensure_ascii=False)
