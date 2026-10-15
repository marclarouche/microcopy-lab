# Simulated component previews — Milestone 4

## Purpose and workflow
Preview an imported source in its component type, and compare it with a current local AI candidate or a clearly labeled human-authored example. The preview is an inspection surface, never an approval or source-edit action.

Load/import strings, clear the component filter if needed, and select Preview string. Select Load preview examples to add five fictional PREVIEW-… sources and illustrative candidate pairs. These are not AI output, accepted revisions, or production behavior evidence. Repeated loads do not duplicate source IDs. If an existing source ID has different data, its illustrative candidate is withheld rather than applied to an unrelated source.

The built-in paired fixture has a different schema from CSV/JSON catalogs: use its load button, not the catalog uploader. Standard CSV/JSON imports continue to contain source strings only. Without a candidate, the original still previews offline. Without Ollama or with invalid optional AI settings, previews remain usable. With a fresh AI result, select the matching source/candidate to compare its pending wording.

Changing source/candidate defaults the view to side-by-side when possible; changing only layout/theme preserves the selected view. Views are Side by side, Original, and Revised. Frame sizes are 260/360/520 CSS pixels, subject to the browser column's available width. Themes are light and dark. The tooltip/helper panel can expand/collapse with native HTML details. Buttons/fields are disabled, and the warning/onboarding templates expose no real product actions.

## Five templates
| Component type | Preview |
| --- | --- |
| button | Disabled action button inside a neutral action area |
| field_label | Literal label linked to a disabled illustrative input |
| tooltip | Disabled sample field and expandable helper panel |
| error_warning | Notice panel with literal message text |
| onboarding_empty_state | Centered empty-state panel with neutral decoration |

The chrome is intentionally neutral and does not assert unsupported product actions or recovery behavior. Rationale, context and provenance appear as plain text outside the simulated component. Illustrative and AI candidates are distinctly labeled. No acceptance controls or automatic source replacements exist.

## Character and layout metrics
Character usage is the exact source/candidate code-point count and uses source max_chars when supplied, otherwise the component guide limit. Escaped HTML expansion is not counted as source characters. Overlength text is retained and flagged for inspection.

Layout fit is a separate advisory estimate. It counts wide characters as two display cells, ignores combining/format marks, uses four-column tabs, and respects explicit newlines. An assumed seven-pixel display cell and per-template padding estimate the number of wrapped lines at the chosen frame width. Visible budgets are one line for a button, two for a label, four for helper/notice text, and six for onboarding content. Templates clip long content within those illustrative budgets; Full original/revised text retains the complete literal string.

This estimate does not measure browser glyph widths or word wrapping. Emoji sequences, proportional fonts, scripts, zoom and responsive column shrinkage can change fit. Even a preview without a warning does not establish production text fit, accessibility compliance, accessible names, keyboard support or user comprehension. Source punctuation/tokens remain unchanged; whitespace uses pre-wrap for display, with the raw original preserved separately.

## Safety and freshness
`src/microcopy_lab/preview_models.py` contains pure typed snapshot/fit logic and fixture validation. It imports no Streamlit, performs no network/filesystem work, and does not call AI. `ui/preview_panel.py` owns presentation, fixed HTML/CSS, widgets and file reading. Mypy covers both layers.

Every source/candidate string is escaped using html.escape before insertion into a text node. Source values never populate styles, attributes, IDs, URLs, paths or executable templates. CSS is static and scoped to the preview class, with allowlisted layout/theme enums. No scripts, remote fonts/assets, links, images, iframe resources, model tools or product actions are included. The app uses [Streamlit's sanitized st.html renderer](https://docs.streamlit.io/develop/api-reference/text/st.html) with JavaScript left disabled; it does not use unsafe_allow_html or the deprecated raw iframe HTML API.

The preview builder recomputes placeholder integrity rather than trusting protected_tokens_valid from a revision. Missing/renamed/duplicated/added tokens, absent source-token declarations, blank candidates, and foreign source IDs withhold the revised component. Configured character-limit violations stay visible with warnings because this is an evaluation surface, not an acceptance gate. The AI safety gate continues to apply stricter candidate acceptance before previews receive AI candidates.

Only AI candidates from the currently displayed, matching input fingerprint are handed to the preview panel. Changes to project/guide/model/settings/selection hide stale AI revisions. Illustrative examples must match the entire current source record. Layout/theme changes do not call Ollama or mutate source/revision data.

## Fixtures and API
`samples/fleetops_preview_examples.json` contains five explicitly human-authored pairs, one per component, including a protected `{report_id}` token. The loader is bounded to 128 KiB and 20 pairs, requires unique source/example/revision IDs, and rejects mismatched or invalid tokens. Examples cannot claim model identity, approval or automatic correctness.

```python
from microcopy_lab.preview_models import LayoutSize, build_preview

# source is a validated UIString; candidate is an optional ProposedRevision.
snapshot = build_preview(source, guide, candidate, layout=LayoutSize.COMPACT)
print(snapshot.original.character_count)
print(
    snapshot.revised.may_overflow_layout if snapshot.revised else snapshot.revision_blocked_reason
)
```

The serialized snapshot has schema version 1.0 and preview version preview-1.0. A future native interface can render the same source-linked data differently without importing Streamlit. Preview schemas document API/fixture structures; they are not final report exports.

## Milestone 5 integration
The preview also accepts retained current editorial drafts, including manual revisions and human edits to AI candidates. The candidate selector shows each draft’s actual review status. Previewing never changes that status. Illustrative fixture comparisons stay labeled illustrative; the separate Add illustrative examples to review action creates pending review entries. See editorial_review.md.
