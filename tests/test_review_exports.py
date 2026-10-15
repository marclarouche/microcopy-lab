"""Version-specific approvals, safe reports, and a complete offline editorial session."""

import csv
import io
import json
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from microcopy_lab.config import load_style_guide
from microcopy_lab.exporters import build_report, export_csv, export_json, export_markdown
from microcopy_lab.models import Project, ProposedRevision, ReviewStatus, UIString
from microcopy_lab.review import (
    create_entry,
    is_current,
    rebase_entry,
    update_entry,
)

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def setup():
    guide = load_style_guide(ROOT / "config/ux_style_guide.yaml")
    source = UIString(
        string_id="REVIEW-1",
        component_type="button",
        original_text="Proceed",
        context="Submit a draft for supervisor review",
        product_behavior="Submit a draft report for supervisor review.",
        extra_metadata={"literal": "<script>test</script>"},
    )
    project = Project(name="Editorial demo", strings=[source])
    revision = ProposedRevision(
        string_id=source.string_id,
        suggested_text="Submit report",
        rationale="Names the verified action",
        category="clarity",
        model_identifier="test-local-model",
    )
    entry = create_entry(project, guide, revision, origin="ai_assisted")
    return project, guide, entry


def decide(project, guide, entry, status=ReviewStatus.APPROVED, **overrides):
    args = {
        "text": entry.revision.suggested_text,
        "rationale": entry.revision.rationale,
        "notes": "Verified with product owner",
        "status": status,
        "behavior_confirmed": True,
        "others": [],
    }
    args.update(overrides)
    return update_entry(entry, project, guide, **args)


@pytest.mark.parametrize("status", list(ReviewStatus))
def test_all_review_states_are_explicit(setup, status):
    project, guide, entry = setup
    updated = decide(project, guide, entry, status)
    assert updated.revision.review_status == status
    assert entry.revision.review_status == ReviewStatus.PENDING
    assert updated.notes == "Verified with product owner"


def test_untrusted_candidate_cannot_import_approval(setup):
    project, guide, entry = setup
    candidate = entry.revision.model_copy(
        update={"review_status": ReviewStatus.APPROVED, "protected_tokens_valid": True}
    )
    result = create_entry(project, guide, candidate, origin="ai_assisted")
    assert result.revision.review_status == ReviewStatus.PENDING
    assert not result.behavior_confirmed


@pytest.mark.parametrize(
    "field,value", [("text", "Submit draft"), ("rationale", "A corrected rationale")]
)
def test_material_edits_reset_approved_version_and_confirmation(setup, field, value):
    project, guide, entry = setup
    approved = decide(project, guide, entry)
    edited = decide(project, guide, approved, **{field: value})
    assert edited.version == 2
    assert edited.revision.review_status == ReviewStatus.PENDING
    assert not edited.behavior_confirmed
    assert approved.version == 1
    assert approved.revision.review_status == ReviewStatus.APPROVED
    assert project.strings[0].original_text == "Proceed"
    assert decide(project, guide, edited).revision.review_status == ReviewStatus.APPROVED


def test_notes_only_change_preserves_approval(setup):
    project, guide, entry = setup
    approved = decide(project, guide, entry)
    edited = decide(project, guide, approved, notes="Additional verification note")
    assert edited.version == 1
    assert edited.revision.review_status == ReviewStatus.APPROVED


def test_approval_requires_human_confirmation(setup):
    project, guide, entry = setup
    with pytest.raises(ValueError, match="Confirm"):
        decide(project, guide, entry, behavior_confirmed=False)


@pytest.mark.parametrize("text", ["Save", "Save {ID}", "Save {id} {id}", "Save {id} {new}"])
def test_broken_tokens_cannot_be_approved_even_if_flag_is_forged(setup, text):
    project, guide, entry = setup
    project.strings[0].original_text = "Save {id}"
    project.strings[0].protected_tokens = ["{id}"]
    candidate = entry.revision.model_copy(
        update={"suggested_text": text, "protected_tokens_valid": True}
    )
    entry = create_entry(project, guide, candidate, origin="manual")
    with pytest.raises(ValueError, match="tokens"):
        decide(project, guide, entry)


def test_overlength_and_protected_product_name_block_approval(setup):
    project, guide, entry = setup
    long = entry.revision.model_copy(update={"suggested_text": "x" * 25})
    with pytest.raises(ValueError, match="character limit"):
        decide(project, guide, create_entry(project, guide, long, origin="manual"))
    project.strings[0].original_text = "FleetOps"
    guide.protected_terms = ["FleetOps"]
    with pytest.raises(ValueError, match="product terms"):
        decide(project, guide, rebase_entry(entry, project, guide))


@pytest.mark.parametrize("mutation", ["source", "context", "guide", "metadata"])
def test_stale_approval_is_excluded_until_explicit_rebase_and_review(setup, mutation):
    project, guide, entry = setup
    approved = decide(project, guide, entry)
    if mutation == "source":
        project.strings[0].original_text = "Continue"
    elif mutation == "context":
        project.product_context = "New verified behavior"
    elif mutation == "guide":
        guide.version = "2.0"
    else:
        project.strings[0].design_notes = "Changed source metadata"
    assert not is_current(approved, project, guide)
    report = build_report(project, guide, [approved])
    assert not report["approved_replacements"]
    assert report["reviews"][0]["stale"]
    assert report["reviews"][0]["revision"]["review_status"] == "pending"
    with pytest.raises(ValueError, match="changed"):
        decide(project, guide, approved)
    rebased = rebase_entry(approved, project, guide)
    assert is_current(rebased, project, guide)
    assert rebased.version == 2
    assert rebased.revision.review_status == ReviewStatus.PENDING
    assert not rebased.behavior_confirmed


def test_adding_another_source_does_not_invalidate_existing_decision(setup):
    project, guide, entry = setup
    project.strings.append(
        UIString(
            string_id="OTHER",
            component_type="button",
            original_text="Cancel",
            context="Cancel form",
        )
    )
    assert is_current(entry, project, guide)


def test_conflicting_approvals_are_rejected_and_export_rechecks(setup):
    project, guide, entry = setup
    approved = decide(project, guide, entry)
    another = create_entry(
        project,
        guide,
        ProposedRevision(
            string_id="REVIEW-1", suggested_text="Submit draft", rationale="Names action"
        ),
        origin="manual",
    )
    with pytest.raises(ValueError, match="Another revision"):
        decide(project, guide, another, others=[approved])
    forged = decide(project, guide, another)
    with pytest.raises(ValueError, match="Only one"):
        build_report(project, guide, [approved, forged])


def test_exports_preserve_ids_metadata_unicode_and_separate_approved(setup):
    project, guide, entry = setup
    project.name = "Éditorial 🛠"
    before = project.model_dump_json()
    approved = decide(project, guide, entry)
    report = build_report(project, guide, [approved])
    parsed = json.loads(export_json(report))
    assert parsed["project"]["strings"][0]["extra_metadata"] == {"literal": "<script>test</script>"}
    assert parsed["approved_replacements"][0]["replacement_text"] == "Submit report"
    assert parsed["reviews"][0]["revision"]["model_identifier"] == "test-local-model"
    rows = list(csv.DictReader(io.StringIO(export_csv(report))))
    assert rows[0]["string_id"] == "REVIEW-1"
    assert rows[0]["review_status"] == "approved"
    assert rows[0]["approved_text"] == "Submit report"
    assert (
        json.loads(rows[0]["source_metadata"])["extra_metadata"]["literal"]
        == "<script>test</script>"
    )
    assert project.model_dump_json() == before
    assert "&lt;script&gt;" in export_markdown(report)


@pytest.mark.parametrize(
    "status", [ReviewStatus.PENDING, ReviewStatus.REJECTED, ReviewStatus.NEEDS_CLARIFICATION]
)
def test_unapproved_copy_never_leaks_into_approved_export(setup, status):
    project, guide, entry = setup
    report = build_report(project, guide, [decide(project, guide, entry, status)])
    assert report["approved_replacements"] == []
    assert len(list(csv.DictReader(io.StringIO(export_csv(report, approved_only=True))))) == 0
    assert next(iter(csv.DictReader(io.StringIO(export_csv(report)))))["approved_text"] == ""


@pytest.mark.parametrize(
    "payload",
    ['=HYPERLINK("https://invalid.example")', "+SUM(1,2)", "-1+2", "@SUM(A1)", " \t=1+1", "\n=1+1"],
)
def test_csv_neutralizes_formula_cells_and_json_remains_exact(setup, payload):
    project, guide, _entry = setup
    project.name = payload
    project.strings[0].original_text = payload
    report = build_report(project, guide, [])
    row = next(iter(csv.DictReader(io.StringIO(export_csv(report)))))
    assert row["original_text"].startswith("'")
    assert json.loads(export_json(report))["project"]["strings"][0]["original_text"] == payload


def test_markdown_cannot_render_source_images_links_or_html(setup):
    project, guide, _entry = setup
    project.strings[
        0
    ].original_text = '![image](https://invalid.example/pixel)<img src="https://invalid.example">'
    text = export_markdown(build_report(project, guide, []))
    assert "![image]" not in text
    assert "<img" not in text
    assert r"\!\[image\]" in text


def test_report_covers_no_revision_sources_and_fresh_summary(setup):
    project, guide, entry = setup
    project.strings.append(
        UIString(
            string_id="TOO-LONG", component_type="button", original_text="x" * 30, context="Test"
        )
    )
    report = build_report(project, guide, [entry])
    assert report["summary"]["total_strings"] == 2
    assert report["summary"]["strings_analyzed"] == 2
    assert report["summary"]["character_limit_violations"] == 1
    assert report["summary"]["failed_analysis_count"] == 0
    assert {r["string_id"] for r in csv.DictReader(io.StringIO(export_csv(report)))} == {
        "REVIEW-1",
        "TOO-LONG",
    }
    assert "TOO\\-LONG" in export_markdown(report)


def element(at, group, label):
    return next(item for item in getattr(at, group) if item.label == label)


def test_complete_offline_manual_review_edit_approve_export_and_preview(setup):
    project, _guide, _entry = setup
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=15)
    at.session_state.project = project
    at.run()
    assert not at.exception
    element(at, "text_area", "New replacement text").input("Submit report")
    element(at, "text_area", "Revision rationale").input("Names the verified action")
    element(at, "button", "Create pending revision").click().run()
    assert not at.exception
    assert len(at.session_state.review_entries) == 1
    element(at, "checkbox", "I verified that this replacement preserves product behavior").check()
    element(at, "selectbox", "Review decision").select("approved")
    element(at, "button", "Save revision and decision").click().run()
    assert not at.exception
    assert at.session_state.review_entries[0].revision.review_status == ReviewStatus.APPROVED
    assert any("Approved: 1" in item.value for item in at.markdown)
    assert "Submit report" in at.get("html")[1].proto.body
    element(at, "text_area", "Replacement text").input("Submit draft")
    element(at, "button", "Save revision and decision").click().run()
    assert not at.exception
    updated = at.session_state.review_entries[0]
    assert updated.version == 2
    assert updated.revision.review_status == ReviewStatus.PENDING
    assert not updated.behavior_confirmed
    assert at.session_state.project.strings[0].original_text == "Proceed"
    assert len(at.get("download_button")) == 4


def test_export_rechecks_forged_approval_and_duplicate_revision_ids(setup):
    project, guide, entry = setup
    forged = entry.model_copy(deep=True)
    forged.revision.review_status = ReviewStatus.APPROVED
    report = build_report(project, guide, [forged])
    assert not report["approved_replacements"]
    assert report["reviews"][0]["revision"]["review_status"] == "pending"
    with pytest.raises(ValueError, match="unique"):
        build_report(project, guide, [entry, entry])


def test_report_ai_partial_failures_and_stale_source_guard(setup):
    from microcopy_lab.ai_models import AIAnalysisResult, AIDiagnostic, AIRecordResult
    from microcopy_lab.engine import audit_fingerprint

    project, guide, entry = setup
    ai = AIAnalysisResult(
        project_id=project.project_id,
        model_identifier="local-test",
        model_digest="test-digest",
        style_guide_version=guide.version,
        application_version="0.5.0",
        prompt_version="test",
        source_fingerprint=audit_fingerprint(project, guide),
        input_fingerprint="selection-and-settings",
        requested_ids=["REVIEW-1"],
        records=[
            AIRecordResult(
                string_id="REVIEW-1",
                status="partial",
                diagnostics=[AIDiagnostic(code="invalid_candidate", message="Candidate withheld.")],
            )
        ],
        status="partial",
        analyzed_count=1,
        failed_count=0,
        partial_count=1,
        clarification_count=0,
    )
    report = build_report(project, guide, [entry], ai=ai)
    assert report["summary"]["partial_analysis_count"] == 1
    assert report["ai_analysis"]["model_digest"] == "test-digest"
    assert "Candidate withheld" in export_markdown(report)
    project.product_context = "Changed context"
    with pytest.raises(ValueError):
        build_report(project, guide, [entry], ai=ai)


def test_human_edit_retains_initial_ai_provenance(setup):
    project, guide, entry = setup
    edited = decide(project, guide, entry, text="Submit draft")
    assert edited.edited_by_human
    assert edited.initial_revision.suggested_text == "Submit report"
    assert edited.initial_revision.model_identifier == "test-local-model"
    report = build_report(project, guide, [edited])
    assert report["reviews"][0]["initial_revision"]["suggested_text"] == "Submit report"
    assert next(csv.DictReader(io.StringIO(export_csv(report))))["edited_by_human"] == "True"


def test_ui_reject_clarify_notes_and_token_error_leave_saved_state_intact(setup):
    project, guide, entry = setup
    project.strings[0].original_text = "Save {id}"
    entry = create_entry(project, guide, entry.revision, origin="manual")
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=15)
    at.session_state.project = project
    at.session_state.review_entries = [entry]
    at.run()
    for status in ["rejected", "needs_clarification"]:
        element(at, "selectbox", "Review decision").select(status)
        element(at, "text_area", "Review notes").input("Ask product owner about the missing token")
        element(at, "button", "Save revision and decision").click().run()
        assert not at.exception
        assert at.session_state.review_entries[0].revision.review_status.value == status
    element(at, "checkbox", "I verified that this replacement preserves product behavior").check()
    element(at, "selectbox", "Review decision").select("approved")
    element(at, "button", "Save revision and decision").click().run()
    assert not at.exception
    assert any("tokens" in error.value for error in at.error)
    assert (
        at.session_state.review_entries[0].revision.review_status
        == ReviewStatus.NEEDS_CLARIFICATION
    )
    assert at.session_state.project.strings[0].original_text == "Save {id}"
