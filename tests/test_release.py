"""v1 acceptance integration, unavailable-network behavior, and release boundaries."""

import ast
import csv
import io
import json
import runpy
import socket
import sys
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from microcopy_lab.ai_config import load_ai_settings
from microcopy_lab.ai_engine import analyze_project
from microcopy_lab.catalog import edit_source
from microcopy_lab.config import load_style_guide
from microcopy_lab.exporters import build_report, export_csv, export_json
from microcopy_lab.importers import import_catalog
from microcopy_lab.models import Project, ProposedRevision, ReviewStatus
from microcopy_lab.review import create_entry, is_current, rebase_entry, update_entry

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def data():
    guide = load_style_guide(ROOT / "config/ux_style_guide.yaml")
    imported = import_catalog(
        (ROOT / "samples/guided_test/01-guided-catalog.json").read_bytes(), "json", guide=guide
    )
    return Project(name="Release QA", strings=imported.strings), guide


def widget(at, kind, label):
    return next(item for item in getattr(at, kind) if item.label == label)


def approve(project, guide):
    entry = create_entry(
        project,
        guide,
        ProposedRevision(
            string_id="TEST-001",
            suggested_text="Submit report",
            rationale="Verified submission action",
        ),
        origin="manual",
    )
    return update_entry(
        entry,
        project,
        guide,
        text=entry.revision.suggested_text,
        rationale=entry.revision.rationale,
        notes="Verified",
        status=ReviewStatus.APPROVED,
        behavior_confirmed=True,
        others=[],
    )


def test_edit_source_preserves_id_extensions_and_is_atomic(data):
    project, guide = data
    project.strings[0].__pydantic_extra__["external"] = {"literal": "🛠 <script>alert(1)</script>"}
    before = project.model_dump_json()
    updated = edit_source(
        project,
        guide,
        "TEST-001",
        {"original_text": "Send draft", "context": "Updated verified context"},
    )
    assert project.model_dump_json() == before
    assert updated.strings[0].string_id == "TEST-001"
    assert updated.strings[0].original_text == "Send draft"
    assert (
        updated.strings[0].model_dump()["external"] == project.strings[0].model_dump()["external"]
    )
    assert updated.strings[1:] == project.strings[1:]
    for changes in [
        {"original_text": " "},
        {"max_chars": 0},
        {"string_id": "NEW"},
        {"protected_tokens": [""]},
    ]:
        with pytest.raises(ValueError):
            edit_source(project, guide, "TEST-001", changes)
        assert project.model_dump_json() == before


def test_source_edit_makes_approval_stale_without_discarding_draft(data):
    project, guide = data
    entry = approve(project, guide)
    changed = edit_source(
        project, guide, "TEST-001", {"product_behavior": "Changed product requirements"}
    )
    assert not is_current(entry, changed, guide)
    assert build_report(changed, guide, [entry])["approved_replacements"] == []
    rebased = rebase_entry(entry, changed, guide)
    assert rebased.revision.review_status == ReviewStatus.PENDING
    assert rebased.version == 2 and not rebased.behavior_confirmed


def test_fingerprint_cannot_validate_a_different_retained_source_snapshot(data):
    project, guide = data
    entry = approve(project, guide)
    entry.source.original_text = "Forged earlier source"
    assert not is_current(entry, project, guide)
    assert not build_report(project, guide, [entry])["approved_replacements"]


@pytest.mark.parametrize("prefix", ["\v", "\f", "\x01", "\ufeff\x01 ", "\u2003"])
def test_csv_control_and_unicode_whitespace_formula_prefixes(data, prefix):
    project, guide = data
    value = prefix + "=1+1"
    project.strings[0].original_text = value
    report = build_report(project, guide, [])
    row = next(csv.DictReader(io.StringIO(export_csv(report))))
    assert row["original_text"] == "'" + value
    assert json.loads(export_json(report))["project"]["strings"][0]["original_text"] == value


def test_csv_contains_findings_even_without_a_revision(data):
    project, guide = data
    row = next(csv.DictReader(io.StringIO(export_csv(build_report(project, guide, [])))))
    findings = json.loads(row["finding_details"])
    assert any(f["string_id"] == "TEST-001" and f["category"] == "component" for f in findings)


def test_complete_offline_demo_with_network_forbidden(data, monkeypatch, tmp_path):
    attempts = []

    def forbidden(*args, **kwargs):
        attempts.append(True)
        raise AssertionError("Offline demo attempted a network operation")

    monkeypatch.setattr(socket.socket, "connect", forbidden)
    monkeypatch.setattr(socket, "getaddrinfo", forbidden)
    monkeypatch.setattr(sys, "argv", ["run_demo.py", "--output", str(tmp_path)])
    runpy.run_path(str(ROOT / "scripts/run_demo.py"), run_name="__main__")
    report = json.loads((tmp_path / "review.json").read_text())
    assert report["summary"]["total_strings"] == 9
    assert sum(report["summary"]["findings_by_category"].values()) == 7
    assert report["summary"]["approved_revision_count"] == 1
    assert {r["revision"]["review_status"] for r in report["reviews"]} == {
        s.value for s in ReviewStatus
    }
    assert (
        next(csv.DictReader(io.StringIO((tmp_path / "approved.csv").read_text())))["approved_text"]
        == "Submit report"
    )
    assert not attempts


def test_ai_unavailable_does_not_block_review_and_exports(data, monkeypatch):
    project, guide = data
    attempts = []

    def unavailable(self, address):
        attempts.append(address)
        raise OSError("Simulated unavailable local service")

    monkeypatch.setattr(socket.socket, "connect", unavailable)
    result = analyze_project(
        project, guide, load_ai_settings(ROOT / "config/ai.yaml"), ["TEST-001"]
    )
    assert result.failed_count == 1
    assert attempts and all(address[0] == "127.0.0.1" for address in attempts)
    report = build_report(project, guide, [approve(project, guide)], ai=result)
    assert report["summary"]["failed_analysis_count"] == 1
    assert report["summary"]["approved_revision_count"] == 1
    assert report["approved_replacements"][0]["string_id"] == "TEST-001"


def test_ui_source_edit_and_approval_rebase(data):
    project, guide = data
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=15)
    at.session_state.project = project
    at.session_state.review_entries = [approve(project, guide)]
    at.run()
    assert not at.exception
    widget(at, "text_area", "Source original text").input("Continue")
    widget(at, "button", "Save source changes").click().run()
    assert not at.exception
    assert at.session_state.project.strings[0].original_text == "Continue"
    assert len(at.get("html")) == 1
    assert any("earlier source" in warning.value for warning in at.warning)
    assert at.session_state.review_entries[0].revision.review_status == ReviewStatus.APPROVED
    widget(at, "button", "Rebase draft on current source").click().run()
    assert not at.exception
    assert at.session_state.review_entries[0].revision.review_status == ReviewStatus.PENDING
    assert at.session_state.review_entries[0].version == 2


def test_ui_rejects_invalid_source_edit_without_losing_catalog(data):
    project, _guide = data
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=15)
    at.session_state.project = project
    at.run()
    widget(at, "text_area", "Source context").input(" ")
    widget(at, "button", "Save source changes").click().run()
    assert not at.exception
    assert at.session_state.project == project
    assert any("Source was not changed" in error.value for error in at.error)


def test_ui_session_with_no_network_can_review_preview_and_export(data, monkeypatch):
    project, guide = data
    attempts = []

    def forbidden(*args, **kwargs):
        attempts.append(True)
        raise AssertionError("Offline interface attempted a network operation")

    monkeypatch.setattr(socket.socket, "connect", forbidden)
    monkeypatch.setattr(socket, "getaddrinfo", forbidden)
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=15)
    at.session_state.project = project
    at.session_state.review_entries = [approve(project, guide)]
    at.run()
    assert not at.exception
    assert len(at.get("html")) == 2
    assert len(at.get("download_button")) == 4
    assert any("Approved: 1" in item.value for item in at.markdown)
    assert not attempts


def test_release_security_boundaries():
    for path in (ROOT / "src/microcopy_lab").glob("*.py"):
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                assert all(
                    n.name.split(".")[0] not in {"streamlit", "subprocess"} for n in node.names
                )
            elif isinstance(node, ast.ImportFrom):
                assert (node.module or "").split(".")[0] not in {"streamlit", "subprocess"}
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                assert node.func.id not in {"eval", "exec"}
    settings = (ROOT / ".streamlit/config.toml").read_text()
    assert 'address = "127.0.0.1"' in settings or 'address="127.0.0.1"' in settings
    assert "gatherUsageStats = false" in settings or "gatherUsageStats=false" in settings
    assert 'showErrorDetails = "none"' in settings or 'showErrorDetails="none"' in settings


def test_published_report_schema_matches_actual_export(data):
    from jsonschema import Draft202012Validator

    project, guide = data
    schema = json.loads((ROOT / "schemas/editorial_report.schema.json").read_text())
    Draft202012Validator.check_schema(schema)
    report = build_report(project, guide, [approve(project, guide)])
    Draft202012Validator(schema).validate(json.loads(export_json(report)))
    report["summary"]["approved_revision_count"] = -1
    assert list(Draft202012Validator(schema).iter_errors(report))


def test_source_selector_does_not_carry_another_records_text(data):
    project, _guide = data
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=15)
    at.session_state.project = project
    at.run()
    widget(at, "selectbox", "Source record to edit").select("TEST-004").run()
    assert not at.exception
    assert widget(at, "text_area", "Source original text").value == project.strings[3].original_text
    assert "{report_id}" in widget(at, "text_area", "Source protected tokens (one per line)").value
    widget(at, "button", "Save source changes").click().run()
    assert not at.exception
    assert at.session_state.project == project
