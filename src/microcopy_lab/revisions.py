"""Application-owned validation of untrusted AI candidate revisions."""

import re
from collections import Counter

from microcopy_lab.ai_models import ModelFinding
from microcopy_lab.config import StyleGuide
from microcopy_lab.models import UIString
from microcopy_lab.placeholders import validate_placeholder_integrity
from microcopy_lab.terminology import phrase_matches, protected_spans

# Only grammatical connectors may be introduced without product evidence.
CONNECTORS = frozenset(
    [
        "a",
        "an",
        "the",
        "to",
        "of",
        "for",
        "with",
        "and",
        "or",
        "your",
        "you",
        "this",
        "that",
        "is",
        "are",
        "be",
        "by",
        "in",
        "on",
        "from",
        "please",
    ]
)


def _words(value: str) -> set[str]:
    return {word.casefold() for word in re.findall(r"[\w]+(?:['’][\w]+)?", value)}


def candidate_is_supported(source: UIString, candidate: ModelFinding, guide: StyleGuide) -> bool:
    """Gate candidates using exact evidence, bounded fit, tokens and vocabulary.

    This is a conservative safety filter, not proof of semantic entailment. Every
    accepted candidate still requires explicit human behavior confirmation.
    """
    text, evidence = candidate.suggested_text, candidate.evidence_quote
    behavior = source.product_behavior
    if (
        not text
        or not text.strip()
        or not behavior
        or not behavior.strip()
        or not evidence
        or len(evidence) < 8
        or evidence not in behavior
        or not candidate.rationale
    ):
        return False
    limit = (
        source.max_chars if source.max_chars is not None else guide.limit_for(source.component_type)
    )
    if len(text) > limit or text == source.original_text:
        return False
    if not validate_placeholder_integrity(source, text, syntaxes=guide.placeholder_syntaxes).valid:
        return False
    for term in guide.protected_terms:
        if Counter(m.text for m in phrase_matches(source.original_text, term)) != Counter(
            m.text for m in phrase_matches(text, term)
        ):
            return False
    candidate_source = source.model_copy(update={"original_text": text})
    spans = protected_spans(candidate_source, guide)
    if any(phrase_matches(text, term, spans) for term in guide.terminology):
        return False
    if any(phrase_matches(text, phrase, spans) for phrase in guide.prohibited_phrases):
        return False
    # Ground in the quoted evidence, not unrelated notes or arbitrary metadata.
    allowed = _words(source.original_text) | _words(evidence) | CONNECTORS
    for discouraged, preferred in guide.terminology.items():
        if phrase_matches(source.original_text, discouraged, protected_spans(source, guide)):
            allowed |= _words(preferred)
    negations = {
        "not",
        "never",
        "no",
        "cannot",
        "can't",
        "won't",
        "don't",
        "doesn't",
        "isn't",
        "aren't",
        "without",
        "must",
        "didn't",
        "shouldn't",
        "couldn't",
        "wouldn't",
        "mustn't",
        "only",
        "always",
        "permanently",
        "temporarily",
    }
    negations |= {word.replace("'", "’") for word in negations}
    original_negations = Counter(
        word.casefold()
        for word in re.findall(r"[\w]+(?:['’][\w]+)?", source.original_text)
        if word.casefold() in negations
    )
    candidate_negations = Counter(
        word.casefold()
        for word in re.findall(r"[\w]+(?:['’][\w]+)?", text)
        if word.casefold() in negations
    )
    if original_negations and original_negations != candidate_negations:
        return False
    evidence_negations = Counter(
        word.casefold()
        for word in re.findall(r"[\w]+(?:['’][\w]+)?", evidence)
        if word.casefold() in negations
    )
    if evidence_negations and evidence_negations != candidate_negations:
        return False
    original_numbers = Counter(re.findall(r"\d+(?:[.,]\d+)*", source.original_text))
    if original_numbers and original_numbers != Counter(re.findall(r"\d+(?:[.,]\d+)*", text)):
        return False
    return _words(text) <= allowed
