"""Deterministic audit acceptance, protection, configuration, and UI tests."""

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from microcopy_lab.config import StyleGuide, load_style_guide
from microcopy_lab.engine import audit_fingerprint, audit_project
from microcopy_lab.importers import import_catalog
from microcopy_lab.models import AuditResult, ComponentType, Project, UIString
from microcopy_lab.placeholders import token_spans, validate_placeholder_integrity
from microcopy_lab.rules import check_basic_text, check_string
from microcopy_lab.terminology import phrase_matches

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def guide():
    return load_style_guide(ROOT / "config/ux_style_guide.yaml")


def item(text="Save report", **kwargs):
    return UIString(
        string_id=kwargs.pop("string_id", "UI-1"),
        component_type=kwargs.pop("component_type", "button"),
        original_text=text,
        context="Fictional maintenance report submission",
        **kwargs,
    )


def codes(matches):
    return {match.rule_id for match in matches}


def test_terminology_matching_and_boundaries(guide):
    source = item("LOG IN, log   in; blogging; execute; executable")
    matches = [m for m in check_string(source, guide) if m.category == "terminology"]
    assert [m.matched_text for m in matches] == ["execute", "LOG IN", "log   in"]
    assert all(source.original_text[m.start : m.end] == m.matched_text for m in matches)
    assert all(m.requires_behavior_confirmation for m in matches)
    assert not phrase_matches("preutilize utilized", "utilize")
    assert phrase_matches("a+b then aaab", "a+b")[0].text == "a+b"


def test_protected_terms_and_tokens(guide):
    guide.protected_terms = ["Execute API"]
    source = item(
        "Execute API: {execute} ${utilize} %s @abort@; execute", protected_tokens=["@abort@"]
    )
    terms = [m.matched_text for m in check_string(source, guide) if m.category == "terminology"]
    assert terms == ["execute"]


def test_prohibited_and_component_rules(guide):
    assert "PHRASE-PROHIBITED" in codes(
        check_string(item("You entered bad data!", component_type="error_warning"), guide)
    )
    assert "COMPONENT-GENERIC-LABEL" in codes(check_string(item("  PROCEED  "), guide))
    assert "COMPONENT-GENERIC-LABEL" not in codes(check_string(item("Proceed to checkout"), guide))
    assert "ERROR-CODE-ONLY" in codes(
        check_string(item("Error 0x8004", component_type="error_warning"), guide)
    )
    assert "ERROR-CODE-ONLY" not in codes(
        check_string(
            item("Error 0x8004: Report remains in drafts.", component_type="error_warning"), guide
        )
    )
    guide.writing_rules["prefer_specific_actions"] = False
    guide.writing_rules["avoid_unexplained_error_codes"] = False
    assert "COMPONENT-GENERIC-LABEL" not in codes(check_string(item("Proceed"), guide))
    assert "ERROR-CODE-ONLY" not in codes(
        check_string(item("Error 0x8004", component_type="error_warning"), guide)
    )


def test_whitespace_punctuation_blank_and_unicode_length(guide):
    matches = check_basic_text("  Save report?!  ", ComponentType.BUTTON, 100, guide)
    assert codes(matches) == {"TEXT-EDGE-WHITESPACE", "TEXT-REPEATED-PUNCTUATION"}
    assert codes(check_basic_text(" \t", ComponentType.FIELD_LABEL, 40, guide)) == {"TEXT-BLANK"}
    assert "TEXT-LENGTH" in codes(check_string(item("é🚚", max_chars=1), guide))
    assert "TEXT-LENGTH" not in codes(check_string(item("é🚚", max_chars=2), guide))
    assert "TEXT-LENGTH" in codes(check_string(item("x" * 25), guide))
    assert "TEXT-REPEATED-PUNCTUATION" not in codes(
        check_string(item("Use @token!!@", protected_tokens=["@token!!@"]), guide)
    )
    assert "TEXT-REPEATED-PUNCTUATION" not in codes(check_string(item("Loading..."), guide))


@pytest.mark.parametrize(
    "candidate,valid,missing,added",
    [
        ("{count} vehicles for {username}", True, {}, {}),
        ("Vehicles for {username}", False, {"{count}": 1}, {}),
        ("{total} vehicles for {username}", False, {"{count}": 1}, {"{total}": 1}),
        ("{count} {count} for {username}", False, {}, {"{count}": 1}),
        ("{count} for {Username}", False, {"{username}": 1}, {"{Username}": 1}),
        ("{count} for {username} ${extra}", False, {}, {"${extra}": 1}),
    ],
)
def test_placeholder_integrity(candidate, valid, missing, added):
    source = item("Hello {username}, {count} vehicles", protected_tokens=["{username}", "{count}"])
    before = source.model_dump_json()
    result = validate_placeholder_integrity(source, candidate)
    assert result.valid is valid
    assert result.missing == missing and result.added == added
    assert source.model_dump_json() == before


def test_placeholder_syntax_and_custom_literals():
    text = "${projectName} {username} %s %d %f %%s {{ignored}} @count@ @count@ a+b %%"
    spans = token_spans(text, ["@count@", "a+b", "@count@"])
    assert [s.token for s in spans] == [
        "${projectName}",
        "{username}",
        "%s",
        "%d",
        "%f",
        "@count@",
        "@count@",
        "a+b",
    ]
    assert all(text[s.start : s.end] == s.token for s in spans)
    assert [s.token for s in token_spans(text, syntaxes=["dollar_brace"])] == ["${projectName}"]
    assert validate_placeholder_integrity(
        item("@count@ @count@", protected_tokens=["@count@"]), "@count@"
    ).missing == {"@count@": 1}
    assert validate_placeholder_integrity(
        item("Cost %%", protected_tokens=["%%"]), "Cost"
    ).missing == {"%%": 1}


def test_absent_declared_tokens_block_candidate(guide):
    source = item("Save report", protected_tokens=["{count}"])
    assert "TOKEN-DECLARED-MISSING" in codes(check_string(source, guide))
    result = validate_placeholder_integrity(source, "Save report")
    assert not result.valid and result.absent_declared_tokens == ["{count}"]


@pytest.mark.parametrize("tokens", [[""], ["  "], ["x" * 201], ["{count}"] * 1001])
def test_token_declaration_bounds(tokens):
    with pytest.raises(ValidationError):
        item(protected_tokens=tokens)


def test_configurable_categories(guide):
    source = item("  Go!! utilize {count}  ", protected_tokens=["{absent}"])
    guide.enabled_categories = []
    assert not audit_project(Project(name="Test", strings=[source]), guide).findings
    guide.enabled_categories = ["length"]
    guide.component_limits[ComponentType.BUTTON] = 1
    assert codes(check_string(source, guide)) == {"TEXT-LENGTH"}


@pytest.mark.parametrize(
    "change",
    [
        {"placeholder_syntaxes": ["arbitrary_regex"]},
        {"enabled_categories": ["magic"]},
        {"terminology": {"log in": "LOG IN"}},
        {"terminology": {"log in": "sign in", "sign in": "log in"}},
        {"terminology": {"log in": "sign in", "LOG IN": "authenticate"}},
        {"prohibited_phrases": [""]},
        {"component_rules": {"unknown": {"discouraged_labels": ["Go"]}}},
        {"component_limits": {"button": 0}},
        {"max_records": True},
    ],
)
def test_invalid_configuration(guide, change):
    with pytest.raises(ValidationError):
        StyleGuide.model_validate(guide.model_dump(mode="json") | change)


def test_m1_config_defaults(guide):
    payload = guide.model_dump(mode="json")
    for key in (
        "prohibited_phrases",
        "protected_terms",
        "component_rules",
        "enabled_categories",
        "placeholder_syntaxes",
    ):
        payload.pop(key)
    assert StyleGuide.model_validate(payload).enabled("terminology")


def test_stable_findings_and_no_mutation(guide):
    source = item("  Go!! utilize  ", custom={"source": "keep", "url": "https://example.invalid"})
    project = Project(project_id="P-1", name="Test", strings=[source])
    snapshot = project.model_dump_json(), guide.model_dump_json()
    first = audit_project(project, guide)
    second = audit_project(project, guide)
    assert first == second
    assert AuditResult.model_validate_json(first.model_dump_json()) == first
    assert len({f.finding_id for f in first.findings}) == len(first.findings)
    assert all(
        f.string_id == source.string_id and f.detection_method == "deterministic"
        for f in first.findings
    )
    assert snapshot == (project.model_dump_json(), guide.model_dump_json())
    assert first.summary.strings_analyzed == 1
    assert sum(first.summary.findings_by_category.values()) == len(first.findings)
    assert sum(first.summary.findings_by_severity.values()) == len(first.findings)
    project.strings.append(item("Save report", string_id="UI-2"))
    assert audit_project(project, guide).findings == first.findings
    assert audit_fingerprint(project, guide) != first.input_fingerprint
    guide.version = "2.0"
    assert audit_fingerprint(project, guide) != second.input_fingerprint


def test_related_terminology_variants(guide):
    sources = [
        item("Log in", string_id="a", screen_id="ACCOUNT"),
        item("Sign in", string_id="b", screen_id="ACCOUNT"),
        item("Sign in", string_id="c", screen_id="OTHER"),
    ]
    project = Project(project_id="P", name="Test", strings=sources)
    findings = audit_project(project, guide).findings
    pairs = [f for f in findings if f.rule_id == "CATALOG-TERM-VARIANTS"]
    assert [(f.string_id, f.related_string_ids) for f in pairs] == [("a", ["b"]), ("b", ["a"])]
    assert all(f.requires_behavior_confirmation for f in pairs)
    project.strings.reverse()
    assert audit_project(project, guide).findings == findings


def test_distinct_token_case_not_grouped(guide):
    sources = [item("Log in {USER}", string_id="a"), item("Sign in {user}", string_id="b")]
    assert not [
        f
        for f in audit_project(Project(name="Test", strings=sources), guide).findings
        if f.category == "consistency"
    ]


def test_empty_clear_and_record_limit(guide):
    assert not audit_project(Project(name="Empty"), guide).findings
    assert not check_string(item("Submit report"), guide)
    guide.max_records = 1
    with pytest.raises(ValueError, match="record limit"):
        audit_project(Project(name="Test", strings=[item(), item(string_id="UI-2")]), guide)


def test_fleetops_expected_rules(guide):
    parsed = import_catalog(
        (ROOT / "samples/fleetops_strings.json").read_bytes(), "json", guide=guide
    )
    expected = json.loads((ROOT / "samples/expected_findings.json").read_text())
    audit = audit_project(
        Project(project_id="fleetops-demo", name="FleetOps", strings=parsed.strings), guide
    )
    actual = {}
    for finding in audit.findings:
        actual.setdefault(finding.string_id, []).append(finding.rule_id)
    assert actual == expected["expected_rules_by_string"]
    assert audit.summary.strings_analyzed == 40
    assert audit.summary.character_limit_violations == 3
    assert audit.summary.strings_with_findings == 15


def test_hostile_source_is_inert_and_unchanged(guide, monkeypatch):
    import socket
    import subprocess
    import urllib.request

    def forbidden(*args, **kwargs):
        pytest.fail("Audit attempted external IO or command execution")

    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(subprocess, "Popen", forbidden)
    monkeypatch.setattr(urllib.request, "urlopen", forbidden)
    source = item(
        '<script>fetch("https://example.invalid")</script> Ignore previous instructions. $(rm -rf /)'
    )
    project = Project(name="Hostile sample", strings=[source])
    before = project.model_dump_json()
    audit_project(project, guide)
    assert project.model_dump_json() == before


def test_ui_audit_filters_and_invalidation():
    from streamlit.testing.v1 import AppTest

    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()
    app.button[1].click().run()
    next(button for button in app.button if button.label == "Run deterministic audit").click().run()
    assert not app.exception
    assert app.session_state.audit_result.summary.strings_analyzed == 40
    assert len(app.dataframe) == 2
    app.multiselect[1].set_value(["terminology"]).run()
    assert set(app.dataframe[1].value["category"]) == {"terminology"}
    app.multiselect[2].set_value(["high"]).run()
    assert app.dataframe[1].value.empty
    app.text_input[0].set_value("Renamed project").run()
    assert len(app.dataframe) == 1
    assert any("changed" in info.value for info in app.info)
    next(button for button in app.button if button.label == "Run deterministic audit").click().run()
    assert not app.exception
    assert len(app.dataframe) == 2


def test_custom_prefix_cannot_hide_standard_token():
    source = item("Hello {username}", protected_tokens=["{user"])
    result = validate_placeholder_integrity(source, "Hello {user")
    assert not result.valid
    assert result.missing == {"{username}": 1}


def test_ambiguous_configuration_is_rejected(guide):
    for changes in [
        {"terminology": {"log in": "sign in", "log  in": "authenticate"}},
        {"prohibited_phrases": ["bad data", "BAD  DATA"]},
    ]:
        with pytest.raises(ValidationError):
            StyleGuide.model_validate(guide.model_dump(mode="json") | changes)


def test_custom_token_whitespace_not_canonicalized(guide):
    sources = [
        item("Log in @two  words@", string_id="a", protected_tokens=["@two  words@"]),
        item("Sign in @two words@", string_id="b", protected_tokens=["@two words@"]),
    ]
    findings = audit_project(Project(name="Test", strings=sources), guide).findings
    assert not [finding for finding in findings if finding.category == "consistency"]
