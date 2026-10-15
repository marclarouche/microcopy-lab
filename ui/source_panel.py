"""Presentation-only editing of original catalog records."""

import streamlit as st

from microcopy_lab.catalog import edit_source
from microcopy_lab.config import StyleGuide
from microcopy_lab.models import ComponentType, Project


def show_source_editor(project: Project, guide: StyleGuide) -> None:
    """Offer an explicit source edit, preserving review drafts for stale-source review."""
    if not project.strings:
        return
    with st.expander("Edit an existing source record"):
        st.caption(
            "This edits your in-memory source catalog. Its ID and extra metadata stay unchanged. Affected revision decisions become stale until explicitly rebased and reviewed. Original files on disk stay unchanged."
        )
        identifier = st.selectbox("Source record to edit", [s.string_id for s in project.strings])
        source = next(s for s in project.strings if s.string_id == identifier)
        # Source-dependent form keys avoid carrying values from another selected record.
        with st.form("source_edit_" + identifier):
            components = [c.value for c in ComponentType]
            component = st.selectbox(
                "Source component type",
                components,
                index=components.index(source.component_type.value),
            )
            text = st.text_area("Source original text", source.original_text, max_chars=100000)
            context = st.text_area("Source context", source.context, max_chars=100000)
            screen = st.text_input("Source screen identifier", source.screen_id or "")
            area = st.text_input("Source product area", source.product_area or "")
            goal = st.text_input("Source user goal", source.user_goal or "")
            behavior = st.text_area(
                "Source verified product behavior", source.product_behavior or ""
            )
            notes = st.text_area("Source design notes", source.design_notes or "")
            reference = st.text_input("Source reference", source.source_reference or "")
            tokens = st.text_area(
                "Source protected tokens (one per line)", "\n".join(source.protected_tokens)
            )
            limit = st.number_input(
                "Source character limit (0 uses style guide)",
                min_value=0,
                max_value=100000,
                value=source.max_chars or 0,
                step=1,
            )
            if st.form_submit_button("Save source changes"):
                optional = {
                    "screen_id": screen,
                    "product_area": area,
                    "user_goal": goal,
                    "product_behavior": behavior,
                    "design_notes": notes,
                    "source_reference": reference,
                }
                # Preserve None versus blank, and existing multiline token declarations,
                # when a field has not actually changed.
                changes: dict[str, object] = {
                    name: value if value != (getattr(source, name) or "") else getattr(source, name)
                    for name, value in optional.items()
                }
                changes.update(
                    component_type=component,
                    original_text=text,
                    context=context,
                    max_chars=int(limit) or None,
                    protected_tokens=source.protected_tokens
                    if tokens == "\n".join(source.protected_tokens)
                    else tokens.splitlines(),
                )
                try:
                    updated = edit_source(project, guide, identifier, changes)
                except (ValueError, TypeError):
                    st.error(
                        "Source was not changed. Check required text, component, tokens, and limits."
                    )
                else:
                    if updated != project:
                        st.session_state.project = updated
                        st.session_state.pop("audit_result", None)
                        st.session_state.pop("ai_result", None)
                    st.rerun()
