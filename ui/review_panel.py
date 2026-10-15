"""Editorial forms and download controls, with all decisions delegated to the engine."""

import streamlit as st

from microcopy_lab.ai_models import AIAnalysisResult
from microcopy_lab.config import StyleGuide
from microcopy_lab.exporters import build_report, export_csv, export_json, export_markdown
from microcopy_lab.models import Project, ProposedRevision, ReviewStatus
from microcopy_lab.preview_models import PreviewExample
from microcopy_lab.review import (
    ReviewEntry,
    approval_problems,
    create_entry,
    is_current,
    rebase_entry,
    update_entry,
)


def show_editorial_review(
    project: Project, guide: StyleGuide, candidates: list[ProposedRevision]
) -> list[ProposedRevision]:
    """Retain drafts independently of AI selection and never auto-approve candidates."""
    st.subheader("Editorial review")
    st.caption(
        "Create or edit a replacement, save the draft, then verify behavior and record a decision. Originals stay unchanged. Editing text or rationale resets approval and behavior confirmation."
    )
    entries = [
        ReviewEntry.model_validate_json(e.model_dump_json())
        for e in st.session_state.get("review_entries", [])
    ]
    known = {e.revision.revision_id for e in entries}
    for candidate in candidates:
        if candidate.revision_id not in known:
            entries.append(create_entry(project, guide, candidate, origin="ai_assisted"))
            known.add(candidate.revision_id)
    st.session_state.review_entries = entries
    if not project.strings:
        st.info("Import or manually enter a string to begin review.")
        return []
    with st.expander("Create a manual revision"), st.form("create_revision", clear_on_submit=True):
        source_id = st.selectbox("Revision source", [s.string_id for s in project.strings])
        text = st.text_area("New replacement text", max_chars=100000)
        rationale = st.text_area("Revision rationale", max_chars=100000)
        if st.form_submit_button("Create pending revision"):
            try:
                if not text.strip() or not rationale.strip():
                    raise ValueError("Enter replacement text and a rationale.")
                candidate = ProposedRevision(
                    string_id=source_id,
                    suggested_text=text,
                    rationale=rationale,
                    category="editorial",
                    rule_id="HUMAN-EDITORIAL",
                )
                entries.append(create_entry(project, guide, candidate, origin="manual"))
                st.session_state.review_entries = entries
                st.rerun()
            except ValueError:
                st.error("Enter nonblank replacement text and a rationale within the field limits.")
    examples = st.session_state.get("preview_examples", [])
    if examples and st.button("Add illustrative examples to review"):
        for stored in examples:
            example = PreviewExample.model_validate_json(stored.model_dump_json())
            if example.revision.revision_id not in known and example.source in project.strings:
                entries.append(
                    create_entry(project, guide, example.revision, origin="illustrative")
                )
                known.add(example.revision.revision_id)
        st.session_state.review_entries = entries
        st.rerun()
    if entries:
        ids = [e.revision.revision_id for e in entries]
        labels = {
            e.revision.revision_id: f"{e.revision.string_id} · {e.origin} · v{e.version} · {e.revision.review_status.value} · {e.revision.revision_id}"
            for e in entries
        }
        selected = st.selectbox("Revision to review", ids, format_func=lambda key: labels[key])
        entry = next(e for e in entries if e.revision.revision_id == selected)
        st.text("Original: " + entry.source.original_text)
        st.text("Context: " + entry.source.context)
        st.text(
            "Verified product behavior: "
            + (
                entry.source.product_behavior
                or "Not recorded; verify with the product owner before approving."
            )
        )
        st.text(
            "Origin: " + entry.origin + " · Model: " + (entry.revision.model_identifier or "None")
        )
        if not is_current(entry, project, guide):
            st.warning(
                "This draft refers to earlier source/context/style settings. Its approval is excluded from exports."
            )
            if st.button("Rebase draft on current source"):
                entries[entries.index(entry)] = rebase_entry(entry, project, guide)
                st.session_state.review_entries = entries
                st.rerun()
        # Versioned keys prevent old widget values from silently restoring edited text.
        key = f"review_{selected}_{entry.version}"
        with st.form(key):
            text = st.text_area(
                "Replacement text",
                entry.revision.suggested_text,
                max_chars=100000,
                key=key + "_text",
            )
            rationale = st.text_area(
                "Rationale", entry.revision.rationale, max_chars=100000, key=key + "_rationale"
            )
            notes = st.text_area("Review notes", entry.notes, max_chars=10000, key=key + "_notes")
            confirmed = st.checkbox(
                "I verified that this replacement preserves product behavior",
                entry.behavior_confirmed,
                key=key + "_confirmed",
            )
            statuses = [status.value for status in ReviewStatus]
            status = st.selectbox(
                "Review decision",
                statuses,
                index=statuses.index(entry.revision.review_status.value),
                key=key + "_status",
            )
            if st.form_submit_button("Save revision and decision"):
                try:
                    updated = update_entry(
                        entry,
                        project,
                        guide,
                        text=text,
                        rationale=rationale,
                        notes=notes,
                        status=ReviewStatus(status),
                        behavior_confirmed=confirmed,
                        others=entries,
                    )
                    entries[entries.index(entry)] = updated
                    st.session_state.review_entries = entries
                    st.rerun()
                except ValueError as error:
                    # Core decision errors are app-owned, never include source or parser internals.
                    message = str(error)
                    st.error(
                        message
                        if "validation error" not in message
                        else "Check the replacement, rationale, and notes field limits."
                    )
        for problem in approval_problems(entry, project, guide):
            st.caption("Approval check: " + problem)
    return [e.revision for e in entries if is_current(e, project, guide)]


def show_exports(project: Project, guide: StyleGuide, ai: AIAnalysisResult | None) -> None:
    """Show a complete summary and explicit reports, independent of Ollama availability."""
    st.subheader("Review summary and exports")
    st.caption(
        "Reports include a fresh deterministic audit of the full catalog. AI results are included only when the current settings and selection match. Approved replacements contain one reviewed version per source."
    )
    entries = [
        ReviewEntry.model_validate_json(e.model_dump_json())
        for e in st.session_state.get("review_entries", [])
    ]
    try:
        report = build_report(project, guide, entries, ai=ai)
    except ValueError:
        st.error(
            "Unable to build this report. Check source links, revision identifiers, and conflicting approvals."
        )
        return
    summary = report["summary"]
    st.write(
        f"Strings: {summary['total_strings']} · Analyzed: {summary['strings_analyzed']} · Pending: {summary['pending_review_count']} · Approved: {summary['approved_revision_count']} · Needs clarification: {summary['needs_clarification_count']} · Rejected: {summary['rejected_revision_count']}"
    )
    st.write(
        f"Length violations: {summary['character_limit_violations']} · Failed AI records: {summary['failed_analysis_count']} · Partial AI records: {summary['partial_analysis_count']} · Stale revisions: {summary['stale_revision_count']}"
    )
    st.write("Findings by category", summary["findings_by_category"])
    st.write("Findings by severity", summary["findings_by_severity"])
    st.caption(
        "JSON preserves exact text and metadata. CSV neutralizes formula-like cells with an apostrophe. Downloads do not change your source files."
    )
    st.download_button(
        "Download JSON report", export_json(report), "microcopy-lab-review.json", "application/json"
    )
    st.download_button(
        "Download CSV catalog", export_csv(report), "microcopy-lab-catalog.csv", "text/csv"
    )
    st.download_button(
        "Download Markdown report",
        export_markdown(report),
        "microcopy-lab-review.md",
        "text/markdown",
    )
    st.download_button(
        "Download approved replacements CSV",
        export_csv(report, approved_only=True),
        "microcopy-lab-approved.csv",
        "text/csv",
        disabled=not report["approved_replacements"],
    )
