"""Safe component rendering and Streamlit comparison controls."""

from collections.abc import Callable
from html import escape
from pathlib import Path

import streamlit as st

from microcopy_lab.config import StyleGuide
from microcopy_lab.importers import validate_records
from microcopy_lab.models import ComponentType, ImportResult, Project, ProposedRevision
from microcopy_lab.preview_models import (
    LayoutSize,
    PreviewExample,
    PreviewTheme,
    PreviewVariant,
    build_preview,
    parse_preview_examples,
)

COMPONENT_LABELS = {
    ComponentType.BUTTON: "Button and action area",
    ComponentType.FIELD_LABEL: "Form field and label",
    ComponentType.TOOLTIP: "Tooltip or helper text",
    ComponentType.ERROR_WARNING: "Error or warning alert",
    ComponentType.ONBOARDING_EMPTY_STATE: "Onboarding or empty state",
}
# All styles and attributes are application constants. Source text appears only
# inside an escaped text node; it never supplies CSS, URLs, IDs or attributes.
CSS = """<style>
.mcl-preview{box-sizing:border-box;max-width:100%;border:1px solid var(--mcl-border);border-radius:14px;padding:24px;min-height:220px;font:14px/1.4 system-ui,sans-serif;background:var(--mcl-bg);color:var(--mcl-fg);margin:4px 0 14px}
.mcl-preview *{box-sizing:border-box;font-family:inherit}
.mcl-preview.mcl-light{--mcl-bg:#fff;--mcl-fg:#17253a;--mcl-muted:#526178;--mcl-border:#ccd5e2;--mcl-accent:#264dcc;--mcl-tint:#eef2ff;--mcl-notice:#fff6e5;--mcl-notice-border:#b77900}
.mcl-preview.mcl-dark{--mcl-bg:#142033;--mcl-fg:#edf2fa;--mcl-muted:#b4c2d8;--mcl-border:#50607a;--mcl-accent:#a8baff;--mcl-tint:#263758;--mcl-notice:#342b1c;--mcl-notice-border:#e9b761}
.mcl-preview.mcl-compact{width:260px}.mcl-preview.mcl-comfortable{width:360px}.mcl-preview.mcl-wide{width:520px}
.mcl-preview .mcl-chrome{font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--mcl-muted);margin-bottom:22px}
.mcl-preview .mcl-copy{white-space:pre-wrap;overflow-wrap:anywhere;margin:0;line-height:1.4;tab-size:4;overflow:hidden}
.mcl-preview .mcl-button{border:1px solid var(--mcl-accent);border-radius:7px;padding:10px 8px;max-width:100%;background:var(--mcl-tint);color:var(--mcl-accent);font-size:14px;line-height:1.4;text-align:left;cursor:default}
.mcl-preview .mcl-button .mcl-copy{display:block;max-height:1.4em}
.mcl-preview .mcl-label{display:block;font-weight:600;max-height:2.8em;margin-bottom:8px}
.mcl-preview .mcl-input{width:100%;border:1px solid var(--mcl-border);border-radius:6px;background:var(--mcl-bg);color:var(--mcl-muted);padding:10px;font-size:14px}
.mcl-preview details{margin-top:12px}.mcl-preview summary{color:var(--mcl-accent);cursor:pointer;margin-bottom:8px;font-size:13px}
.mcl-preview .mcl-helper{padding:10px;border-left:3px solid var(--mcl-accent);background:var(--mcl-tint)}
.mcl-preview .mcl-helper .mcl-copy{max-height:5.6em}
.mcl-preview .mcl-alert{padding:14px;border-left:4px solid var(--mcl-notice-border);border-radius:6px;background:var(--mcl-notice)}
.mcl-preview .mcl-alert-title{font-weight:700;margin-bottom:6px}.mcl-preview .mcl-alert .mcl-copy{max-height:5.6em}
.mcl-preview .mcl-empty{text-align:center;padding:4px}.mcl-preview .mcl-symbol{font-size:28px;color:var(--mcl-accent);margin-bottom:12px}.mcl-preview .mcl-empty .mcl-copy{max-height:8.4em}
</style>"""


def render_component(
    variant: PreviewVariant, component: ComponentType, layout: LayoutSize, theme: PreviewTheme
) -> str:
    """Render only escaped literal text inside fixed, scoped component markup."""
    text = escape(variant.text, quote=True)
    if component == ComponentType.BUTTON:
        content = (
            '<button class="mcl-button" type="button" disabled><span class="mcl-copy">'
            + text
            + "</span></button>"
        )
    elif component == ComponentType.FIELD_LABEL:
        field_id = "mcl-field-original" if variant.version == "original" else "mcl-field-revised"
        content = (
            f'<label class="mcl-label mcl-copy" for="{field_id}">'
            + text
            + f'</label><input id="{field_id}" class="mcl-input" placeholder="Example input" disabled>'
        )
    elif component == ComponentType.TOOLTIP:
        content = (
            '<input class="mcl-input" aria-label="Illustrative input" placeholder="Example field" disabled><details open><summary>About this field</summary><div class="mcl-helper"><div class="mcl-copy">'
            + text
            + "</div></div></details>"
        )
    elif component == ComponentType.ERROR_WARNING:
        content = (
            '<div class="mcl-alert" role="note"><div class="mcl-alert-title">Notice</div><div class="mcl-copy">'
            + text
            + "</div></div>"
        )
    else:
        content = (
            '<div class="mcl-empty"><div class="mcl-symbol" aria-hidden="true">○</div><div class="mcl-copy">'
            + text
            + "</div></div>"
        )
    return (
        CSS
        + f'<section class="mcl-preview mcl-{layout.value} mcl-{theme.value}" aria-label="Simulated component"><div class="mcl-chrome">Illustrative interface</div>{content}</section>'
    )


def _show_variant(
    variant: PreviewVariant, component: ComponentType, layout: LayoutSize, theme: PreviewTheme
) -> None:
    st.markdown("**Original**" if variant.version == "original" else "**Revised**")
    st.html(render_component(variant, component, layout, theme))
    st.text(
        f"{variant.character_count} / {variant.max_chars} characters · Estimated lines: {variant.estimated_lines} / {variant.visible_lines}"
    )
    if variant.exceeds_character_limit:
        st.warning("Exceeds the configured character limit.")
    if variant.may_overflow_layout:
        st.warning("May be clipped or wrap beyond this illustrative layout. Try a wider frame.")
    if variant.tokens:
        st.text(
            "Protected tokens: "
            + ", ".join(f"{token} ×{count}" for token, count in variant.tokens.items())
        )
    with st.expander(
        "Full original text" if variant.version == "original" else "Full revised text"
    ):
        st.text(variant.text)


def show_preview_panel(
    project: Project,
    guide: StyleGuide,
    revisions: list[ProposedRevision],
    selected_components: list[str],
    *,
    sample_path: Path,
    accept: Callable[[ImportResult], None],
) -> None:
    """Inspect source or current AI/illustrative candidates without applying edits."""
    st.subheader("Component previews")
    st.caption(
        "Simulated layouts only. They do not prove production text fit, behavior, or accessibility compliance. Preview actions are inert."
    )
    st.caption(
        "Load the examples once, then choose Preview string below. The preview selector is separate from the AI review selection."
    )
    if st.button("Load preview examples"):
        already_loaded = bool(st.session_state.get("preview_examples"))
        try:
            with sample_path.open("rb") as handle:
                data = handle.read(131_073)
            examples = parse_preview_examples(data, guide)
            result = validate_records(
                [example.source.model_dump() for example in examples],
                guide=guide,
                existing=project.strings,
            )
            accept(result)
            if not result.fatal:
                st.session_state.preview_examples = examples
                if examples and not already_loaded:
                    st.session_state.preview_source_id = examples[0].source.string_id
            st.rerun()
        except (OSError, ValueError):
            st.error(
                "Unable to load the local preview examples. Check their source links and protected tokens."
            )
    sources = [
        source
        for source in project.strings
        if not selected_components or source.component_type.value in selected_components
    ]
    if not sources:
        st.info("Load/import strings or clear the component filter to inspect previews.")
        return
    identifiers = [source.string_id for source in sources]
    if st.session_state.get("preview_source_id") not in identifiers:
        st.session_state.preview_source_id = identifiers[0]
    identifier = st.selectbox("Preview string", identifiers, key="preview_source_id")
    source = next(source for source in sources if source.string_id == identifier)
    st.text(COMPONENT_LABELS[source.component_type])
    st.text("Context: " + source.context)
    candidates: list[tuple[str, ProposedRevision]] = [
        ("Review draft · " + revision.revision_id + " · " + revision.review_status.value, revision)
        for revision in revisions
        if revision.string_id == identifier
    ]
    examples = st.session_state.get("preview_examples", [])
    for stored_example in examples:
        # Revalidate persisted example data after live reloads; an old model
        # instance is not isinstance() the newly loaded model class.
        try:
            example = PreviewExample.model_validate_json(stored_example.model_dump_json())
        except (AttributeError, TypeError, ValueError):
            st.info("A stored example needs reloading. Select Load preview examples to refresh it.")
            continue
        if example.source.string_id == identifier:
            if example.source == source:
                candidates.append(
                    ("Illustrative example · " + example.example_id, example.revision)
                )
            else:
                st.info(
                    "The example source differs from this catalog record; its illustrative candidate is withheld."
                )
    revision = None
    if candidates:
        labels = [label for label, _ in candidates]
        if st.session_state.get("preview_candidate") not in labels:
            st.session_state.preview_candidate = labels[0]
        chosen = st.selectbox("Preview candidate", labels, key="preview_candidate")
        revision = next(candidate for label, candidate in candidates if label == chosen)
        st.text(
            "Illustrative, human-authored comparison — not AI output or approval."
            if chosen.startswith("Illustrative")
            else "Review draft · Status: " + revision.review_status.value
        )
        st.text("Rationale: " + revision.rationale)
    else:
        st.info(
            "No current candidate for this source. Load preview examples or run local AI review to compare versions."
        )
    settings_columns = st.columns(2)
    with settings_columns[0]:
        layout = LayoutSize(
            st.selectbox(
                "Preview frame", [size.value for size in LayoutSize], index=1, key="preview_layout"
            )
        )
    with settings_columns[1]:
        theme = PreviewTheme(
            st.selectbox(
                "Preview theme", [value.value for value in PreviewTheme], key="preview_theme"
            )
        )
    modes = ["Side by side", "Original", "Revised"] if revision else ["Original"]
    pair = (source.string_id, revision.revision_id if revision else None)
    if (
        st.session_state.get("preview_active_pair") != pair
        or st.session_state.get("preview_mode") not in modes
    ):
        st.session_state.preview_mode = modes[0]
        st.session_state.preview_active_pair = pair
    mode = st.radio("Preview view", modes, horizontal=True, key="preview_mode")
    try:
        comparison = build_preview(source, guide, revision, layout=layout)
    except ValueError:
        st.error("Unable to preview this record. Check its source and protected-token metadata.")
        return
    st.caption(
        f"Selected frame: {comparison.frame_width_px} px; narrow browser columns may shrink it. Fit estimates use display-cell widths, not browser measurements."
    )
    if comparison.revision_blocked_reason:
        st.warning("Revised preview withheld: " + comparison.revision_blocked_reason)
    if mode == "Side by side":
        left, right = st.columns(2)
        with left:
            _show_variant(comparison.original, source.component_type, layout, theme)
        with right:
            if comparison.revised:
                _show_variant(comparison.revised, source.component_type, layout, theme)
    elif mode == "Original":
        _show_variant(comparison.original, source.component_type, layout, theme)
    elif comparison.revised:
        _show_variant(comparison.revised, source.component_type, layout, theme)
