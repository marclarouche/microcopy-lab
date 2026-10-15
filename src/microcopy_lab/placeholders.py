"""Literal placeholder discovery and multiset integrity validation."""

import re
from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass

from microcopy_lab.config import DEFAULT_SYNTAXES, TokenSyntax
from microcopy_lab.models import TokenValidation, UIString

PATTERNS: dict[TokenSyntax, str] = {
    "brace": r"(?<![{$])\{[A-Za-z_][A-Za-z0-9_.]*\}(?!})",
    "dollar_brace": r"\$\{[A-Za-z_][A-Za-z0-9_.]*\}",
    "printf": r"%[sdf]",
}


@dataclass(frozen=True)
class TokenSpan:
    """One literal token occurrence with original code-point offsets."""

    token: str
    start: int
    end: int


def token_spans(
    text: str, declared: Sequence[str] = (), *, syntaxes: Sequence[TokenSyntax] = DEFAULT_SYNTAXES
) -> list[TokenSpan]:
    """Find supported tokens and explicitly declared literal tokens once per span."""
    if (
        len(text) > 100_000
        or len(declared) > 1000
        or any(not t.strip() or len(t) > 200 for t in declared)
    ):
        raise ValueError("Placeholder input exceeds supported limits")
    spans: set[tuple[str, int, int]] = set()
    patterns = [PATTERNS[syntax] for syntax in dict.fromkeys(syntaxes)]
    if patterns:
        # Consume escaped percent pairs so %%s cannot be mistaken for %s.
        for match in re.finditer(r"%%|" + "|".join(patterns), text):
            if match[0] != "%%":
                spans.add((match[0], match.start(), match.end()))
    # Explicit declarations are independent of syntax discovery, so a custom
    # prefix cannot hide a recognized token. Identical spans are counted once.
    for literal in sorted(set(declared)):
        for match in re.finditer(re.escape(literal), text):
            spans.add((match[0], match.start(), match.end()))
    return [
        TokenSpan(token, start, end)
        for token, start, end in sorted(spans, key=lambda span: (span[1], -span[2], span[0]))
    ]


def validate_placeholder_integrity(
    source: UIString, candidate: str, *, syntaxes: Sequence[TokenSyntax] = DEFAULT_SYNTAXES
) -> TokenValidation:
    """Reject loss, renaming, duplication, addition, or absent declared tokens.

    This helper does not generate revisions or modify source records. Token order
    may change; spelling, case, and occurrence counts must remain identical.
    """
    original = Counter(
        span.token
        for span in token_spans(source.original_text, source.protected_tokens, syntaxes=syntaxes)
    )
    proposed = Counter(
        span.token for span in token_spans(candidate, source.protected_tokens, syntaxes=syntaxes)
    )
    absent = sorted(
        {token for token in source.protected_tokens if token not in source.original_text}
    )
    missing = dict(sorted((original - proposed).items()))
    added = dict(sorted((proposed - original).items()))
    return TokenValidation(
        valid=not (missing or added or absent),
        missing=missing,
        added=added,
        source_tokens=dict(sorted(original.items())),
        candidate_tokens=dict(sorted(proposed.items())),
        absent_declared_tokens=absent,
    )
