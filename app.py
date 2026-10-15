"""Streamlit presentation layer for the deterministic content audit."""

from collections.abc import Callable
from pathlib import Path

import streamlit as st
import yaml

from microcopy_lab.ai_adapter import AIError, OllamaClient
from microcopy_lab.ai_config import load_ai_settings
from microcopy_lab.ai_engine import ai_fingerprint, analyze_project
from microcopy_lab.ai_models import AIAnalysisResult
from microcopy_lab.config import StyleGuide, load_style_guide
from microcopy_lab.engine import audit_fingerprint, audit_project
from microcopy_lab.importers import import_catalog, validate_records
from microcopy_lab.models import AuditResult, ComponentType, ImportResult, Project, ProposedRevision
from ui.preview_panel import show_preview_panel
from ui.review_panel import show_editorial_review, show_exports
from ui.source_panel import show_source_editor

ROOT = Path(__file__).resolve().parent


def show_ai_review(
    project: Project, guide: StyleGuide, accept: Callable[[ImportResult], None]
) -> list[ProposedRevision]:
    """Render optional local review and return only current candidate revisions."""
    st.session_state.current_ai_result = None
    st.subheader("Local AI review")
    st.caption(
        "Optional Ollama review. Suggestions remain pending and require product behavior confirmation."
    )
    try:
        ai_settings = load_ai_settings(ROOT / "config/ai.yaml")
    except (OSError, ValueError, yaml.YAMLError):
        st.error("Unable to load local AI settings. Deterministic audits remain available.")
        return []
    model_name = st.text_input("Installed Ollama model", ai_settings.model, key="ai_model_name")
    try:
        ai_settings = ai_settings.model_copy(update={"model": model_name})
        ai_settings = type(ai_settings).model_validate(ai_settings.model_dump())
    except ValueError:
        st.error("Enter a supported local model name. Cloud models are not supported.")
        return []
    if st.button("Check local Ollama models"):
        try:
            models = OllamaClient(ai_settings).available_models()
            if models:
                st.text("Installed local models: " + ", ".join(model.name for model in models))
            else:
                st.info(
                    "No supported local-weight models were found. Deterministic audits remain available."
                )
        except AIError as error:
            st.warning(str(error))
    if st.button("Load AI examples"):
        accept(
            import_catalog(
                (ROOT / "samples/fleetops_ai_examples.json").read_bytes(),
                "json",
                guide=guide,
                existing=project.strings,
            )
        )
        st.rerun()
    ai_selected = st.multiselect(
        "Strings for local AI review",
        [item.string_id for item in project.strings],
        key="ai_selected_ids",
    )
    st.caption(
        f"Select up to {ai_settings.max_records_per_run} strings. The AI examples include fictional verified behavior; the original demo may require clarification."
    )
    if st.button("Run local AI review", disabled=not ai_selected):
        if len(ai_selected) > ai_settings.max_records_per_run:
            st.warning("Select fewer strings to stay within the configured AI run limit.")
        else:
            with st.spinner("Reviewing locally with Ollama…"):
                try:
                    st.session_state.ai_result = analyze_project(
                        project, guide, ai_settings, ai_selected
                    )
                except ValueError:
                    st.session_state.pop("ai_result", None)
                    st.error(
                        "Unable to review this selection. Check its identifiers and configured limits."
                    )
    candidates: list[ProposedRevision] = []
    ai_result = st.session_state.get("ai_result")
    if ai_result is not None:
        ai_result = AIAnalysisResult.model_validate_json(ai_result.model_dump_json())
        st.session_state.ai_result = ai_result
        if ai_result.input_fingerprint != ai_fingerprint(project, guide, ai_settings, ai_selected):
            st.info(
                "AI inputs, selection, or settings changed. Run local AI review again to see current results."
            )
        else:
            st.session_state.current_ai_result = ai_result
            candidates = [revision for record in ai_result.records for revision in record.revisions]
            st.text(
                f"Status: {ai_result.status} · Analyzed: {ai_result.analyzed_count} · Failed: {ai_result.failed_count} · Partial: {ai_result.partial_count} · Questions: {ai_result.clarification_count}"
            )
            st.text(
                f"Model: {ai_result.model_identifier} · Digest: {ai_result.model_digest or 'unavailable'} · Prompt: {ai_result.prompt_version}"
            )
            st.dataframe(
                [
                    {"string_id": record.string_id, "status": record.status}
                    for record in ai_result.records
                ],
                width="stretch",
                hide_index=True,
            )
            for record in ai_result.records:
                for diagnostic in record.diagnostics:
                    st.text(f"{record.string_id} · {diagnostic.code}: {diagnostic.message}")
                for question in record.clarifications:
                    st.text(f"{question.string_id} · Clarification: {question.question}")
            st.write("AI findings")
            st.dataframe(
                [
                    finding.model_dump(mode="json")
                    for record in ai_result.records
                    for finding in record.findings
                ],
                width="stretch",
                hide_index=True,
            )
            st.write("Initial AI candidates — editorial decisions are recorded below")
            st.dataframe(
                [
                    revision.model_dump(mode="json")
                    for record in ai_result.records
                    for revision in record.revisions
                ],
                width="stretch",
                hide_index=True,
            )

    return candidates


def main() -> None:
    """Display an ephemeral project and safe plain-text catalog."""
    st.set_page_config(page_title="Microcopy Lab", layout="wide")
    st.title("Microcopy Lab")
    st.caption("Version 1.0 · Audit, revise, review, and export interface copy")
    try:
        guide = load_style_guide(ROOT / "config/ux_style_guide.yaml")
    except (OSError, ValueError, yaml.YAMLError):
        st.error("Unable to load the local style guide. Check its configuration.")
        return
    if "project" not in st.session_state:
        st.session_state.project = Project(name="Untitled project")
    # Keep session records compatible with reloaded Pydantic/enum classes.
    project = Project.model_validate_json(st.session_state.project.model_dump_json())
    st.session_state.project = project
    project.name = st.text_input("Project name", project.name) or "Untitled project"
    project.product_context = st.text_area("Product context", project.product_context)
    st.metric("Catalog strings", len(project.strings))
    st.caption(f"Style guide: {guide.name} {guide.version} · Record limit: {guide.max_records}")

    def accept(result: ImportResult) -> None:
        if not result.fatal:
            project.strings.extend(result.strings)
            if result.strings:
                st.session_state.pop("audit_result", None)
                st.session_state.pop("ai_result", None)
        st.session_state.last_result = result

    with st.expander("Import strings", expanded=True):
        upload = st.file_uploader("CSV or JSON · UTF-8 · maximum 5 MB", type=["csv", "json"])
        if st.button("Import file", disabled=upload is None) and upload is not None:
            accept(
                import_catalog(
                    upload.getvalue(),
                    "csv" if upload.name.lower().endswith(".csv") else "json",
                    guide=guide,
                    existing=project.strings,
                )
            )
        if st.button("Load FleetOps Demo"):
            result = import_catalog(
                (ROOT / "samples/fleetops_strings.json").read_bytes(),
                "json",
                guide=guide,
                existing=project.strings,
            )
            accept(result)
            project.name = "FleetOps Demo"
            project.product_context = "Fictional fleet maintenance SaaS; no real operational data."
            st.rerun()
    with st.form("manual", clear_on_submit=True):
        st.subheader("Manual string entry")
        identifier = st.text_input("String identifier")
        component = st.selectbox("Component type", [c.value for c in ComponentType])
        text = st.text_area("Original text")
        context = st.text_area("User or interface context")
        screen = st.text_input("Screen identifier (optional)")
        area = st.text_input("Product area (optional)")
        goal = st.text_input("User goal (optional)")
        behavior = st.text_area("Verified product behavior (optional)")
        notes = st.text_area("Design notes (optional)")
        reference = st.text_input("Source reference (optional)")
        tokens = st.text_area("Protected tokens (one per line)")
        limit = st.number_input(
            "Character limit (0 uses style guide)", min_value=0, max_value=100000, step=1
        )
        if st.form_submit_button("Add string"):
            accept(
                validate_records(
                    [
                        {
                            "string_id": identifier,
                            "component_type": component,
                            "original_text": text,
                            "context": context,
                            "screen_id": screen or None,
                            "product_area": area or None,
                            "user_goal": goal or None,
                            "product_behavior": behavior or None,
                            "design_notes": notes or None,
                            "source_reference": reference or None,
                            "protected_tokens": tokens.splitlines(),
                            "max_chars": int(limit) or None,
                        }
                    ],
                    guide=guide,
                    existing=project.strings,
                )
            )
    st.subheader("Validation summary")
    last_result = st.session_state.get("last_result")
    if last_result is not None:
        last_result = ImportResult.model_validate_json(last_result.model_dump_json())
        st.session_state.last_result = last_result
        st.write(
            f"Last batch: {len(last_result.strings)} accepted · {last_result.rejected_count} rejected"
        )
        for warning in last_result.warnings:
            st.text(f"{warning.code} · row {warning.row or '—'} · {warning.message}")
    current = validate_records([item.model_dump() for item in project.strings], guide=guide)
    st.write(f"Catalog length warnings: {len(current.warnings)}")
    st.subheader("String catalog")
    selected = st.multiselect("Filter component types", [c.value for c in ComponentType])
    rows = [
        item.model_dump(mode="json")
        for item in project.strings
        if not selected or item.component_type.value in selected
    ]
    st.dataframe(rows, width="stretch", hide_index=True)
    show_source_editor(project, guide)
    st.subheader("Deterministic audit")
    st.caption(
        "Rule matches are advisory. Confirm product meaning before revising. No source strings are changed."
    )
    if st.button("Run deterministic audit", disabled=not project.strings):
        try:
            st.session_state.audit_result = audit_project(project, guide)
        except ValueError:
            st.session_state.pop("audit_result", None)
            st.error(
                "Unable to audit this catalog. Check its record limit and protected-token metadata."
            )
    audit = st.session_state.get("audit_result")
    if audit is not None:
        audit = AuditResult.model_validate_json(audit.model_dump_json())
        st.session_state.audit_result = audit
        if audit.input_fingerprint != audit_fingerprint(project, guide):
            st.info("Project or style guide changed. Run the audit again to see current findings.")
        else:
            summary = audit.summary
            st.write(
                f"Strings analyzed: {summary.strings_analyzed} · Strings with findings: {summary.strings_with_findings} · Findings: {len(audit.findings)} · Length violations: {summary.character_limit_violations}"
            )
            st.text(
                f"Guide: {audit.style_guide_name} {audit.style_guide_version} · Engine: {audit.engine_version}"
            )
            st.write("By category", summary.findings_by_category)
            st.write("By severity", summary.findings_by_severity)
            categories = st.multiselect("Finding categories", sorted(summary.findings_by_category))
            severities = st.multiselect("Finding severities", ["low", "medium", "high"])
            components = {item.string_id: item.component_type.value for item in project.strings}
            findings = [
                finding.model_dump(mode="json")
                for finding in audit.findings
                if (not categories or finding.category in categories)
                and (not severities or finding.severity in severities)
                and (not selected or components[finding.string_id] in selected)
            ]
            st.dataframe(findings, width="stretch", hide_index=True)
            if not audit.findings:
                st.success(
                    "No configured rules matched. This does not establish UX quality or accessibility compliance."
                )

    candidates = show_ai_review(project, guide, accept)
    candidates = show_editorial_review(project, guide, candidates)
    show_preview_panel(
        project,
        guide,
        candidates,
        selected,
        sample_path=ROOT / "samples/fleetops_preview_examples.json",
        accept=accept,
    )

    show_exports(project, guide, st.session_state.get("current_ai_result"))

    st.caption(
        "Session data is held in memory. Reloading or ending the session can discard it. AI output is advisory; no source text is replaced."
    )


if __name__ == "__main__":
    main()
