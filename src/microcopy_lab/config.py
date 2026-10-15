"""Bounded, validated, data-only YAML editorial configuration."""

from pathlib import Path
from typing import Annotated, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

from microcopy_lab.models import ComponentType

Phrase = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
Category = Literal[
    "length",
    "terminology",
    "prohibited_phrase",
    "whitespace",
    "punctuation",
    "component",
    "placeholders",
    "consistency",
]
TokenSyntax = Literal["brace", "dollar_brace", "printf"]
PositiveLimit = Annotated[int, Field(strict=True, gt=0, le=100_000)]

DEFAULT_CATEGORIES: tuple[Category, ...] = (
    "length",
    "terminology",
    "prohibited_phrase",
    "whitespace",
    "punctuation",
    "component",
    "placeholders",
    "consistency",
)
DEFAULT_SYNTAXES: tuple[TokenSyntax, ...] = ("brace", "dollar_brace", "printf")


def normalized_phrase(phrase: str) -> str:
    """Normalize configuration keys for conflict detection, never source copy."""
    return " ".join(phrase.split()).casefold()


class ComponentRules(BaseModel):
    """Exact generic labels to flag for a particular component."""

    model_config = ConfigDict(extra="forbid")
    discouraged_labels: list[Phrase] = Field(default_factory=list, max_length=500)


class StyleGuide(BaseModel):
    """Editorial rules; patterns are literal phrases, never arbitrary regex."""

    model_config = ConfigDict(extra="forbid")
    name: Phrase
    version: Phrase
    audience: Phrase
    voice: dict[str, bool]
    terminology: dict[Phrase, Phrase]
    component_limits: dict[ComponentType, PositiveLimit]
    writing_rules: dict[str, bool]
    max_records: PositiveLimit = 1000
    prohibited_phrases: list[Phrase] = Field(default_factory=list, max_length=500)
    protected_terms: list[Phrase] = Field(default_factory=list, max_length=500)
    component_rules: dict[ComponentType, ComponentRules] = Field(default_factory=dict)
    enabled_categories: list[Category] = Field(default_factory=lambda: list(DEFAULT_CATEGORIES))
    placeholder_syntaxes: list[TokenSyntax] = Field(default_factory=lambda: list(DEFAULT_SYNTAXES))

    @model_validator(mode="after")
    def validate_rules(self) -> "StyleGuide":
        """Require all component limits and unambiguous terminology mappings."""
        if set(self.component_limits) != set(ComponentType):
            raise ValueError("Provide positive limits for all component types")
        keys = [normalized_phrase(key) for key in self.terminology]
        if len(keys) != len(set(keys)) or len(keys) > 500:
            raise ValueError("Terminology keys must be unique ignoring case and bounded")
        if any(
            normalized_phrase(key) == normalized_phrase(value)
            for key, value in self.terminology.items()
        ):
            raise ValueError("A discouraged term must differ from its preferred term")
        if set(keys) & {normalized_phrase(value) for value in self.terminology.values()}:
            raise ValueError("Terminology chains and cycles are unsupported")
        prohibited = [normalized_phrase(phrase) for phrase in self.prohibited_phrases]
        if len(prohibited) != len(set(prohibited)):
            raise ValueError("Prohibited phrases must be unique ignoring case and whitespace")
        return self

    def limit_for(self, component: ComponentType) -> int:
        """Return the configured component limit."""
        return self.component_limits[component]

    def enabled(self, category: Category) -> bool:
        """Check the category switch shared by all deterministic rules."""
        return category in self.enabled_categories


def load_style_guide(path: Path) -> StyleGuide:
    """Read at most 100 KB and load YAML with SafeLoader."""
    with path.open("rb") as handle:
        data = handle.read(100_001)
    if len(data) > 100_000:
        raise ValueError("Style guide exceeds size limit")
    return StyleGuide.model_validate(yaml.safe_load(data.decode("utf-8")))
