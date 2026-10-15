# User guide
1. Install and launch using README.md; run from the repository root so localhost and telemetry settings apply.
2. Enter a project name and product context.
3. Select Load FleetOps Demo, or choose a UTF-8 CSV/JSON file and select Import file. Repeated demo loads report duplicate IDs rather than replacing source data.
4. Read the last-batch validation summary. Valid rows are added, invalid rows are skipped, and fatal file errors leave the catalog unchanged. Character-limit warnings retain source text.
5. Use Manual string entry to add an ID, component, original text, and context. Optional metadata and protected literal tokens are retained. A character limit of 0 selects the style guide default.
6. Filter the catalog by component; no selection shows all strings.
7. Select Run deterministic audit. Read the summary, guide/engine version, category/severity counts, and source-linked findings. The demo produces 15 findings across 40 analyzed strings, including three length violations.
8. Filter findings by category or severity. The catalog component filter also applies to findings. Summary counts always describe the entire audited project.
9. Review rule explanations and related IDs against verified product behavior. No source text changes. A configured match is not proof of a defect; an unmatched string is not a quality or accessibility certification.
10. Change local YAML rules, character limits, or record cap and rerun. If the project or guide changes, stale results are hidden and the UI requests a fresh audit. Imports that add strings clear previous findings.

The FleetOps data is fictional. Hostile examples remain plain text. Token integrity checks are enforced by the AI candidate gate and remain available through the Python engine; editorial decisions and report downloads are available under Editorial review and Review summary and exports. Keep original source files: session data is temporary and reports are not a project reopen format.

## Optional local AI review
Ensure Ollama is already running with an installed local model. Check local Ollama models, or keep the configured installed model name. Load AI examples, select one ID under Strings for local AI review, and select Run local AI review. Begin with AI-DEMO-001; CPU inference can take time.

Read per-record status and diagnostics before examining findings and pending candidate revisions. Missing verified behavior produces questions. Candidate text includes a rationale, source evidence and model traceability, but always needs human behavior confirmation. Original strings remain unchanged. Failed or partial runs do not affect deterministic audits. Changing model/settings, selection, catalog or guide hides stale AI results.

The original FleetOps catalog intentionally contains generic context without verified product_behavior. Use the AI examples for evidence-backed demonstrations, or supply your own verified behavior during manual entry/import. Do not invent behavior merely to obtain a suggestion. See local_ai.md for setup, bounds and limitations.

## Compare in simulated components
Scroll to Component previews and choose a source. Clear the catalog's component filter to see all types. Without a candidate, inspect the original; with a fresh AI candidate, compare versions. For an offline tour, select Load preview examples and switch among PREVIEW-001 through PREVIEW-005. Those pairs are labeled human-authored and unapproved, distinct from AI suggestions.

Use Side by side / Original / Revised, frame size, and light/dark theme controls. Open About this field in the helper template. Review exact character usage, layout estimates, token counts and the Full text disclosure. Length/fit warnings do not apply a change. Broken-token or foreign-source revised previews are withheld. Disabled controls perform no product action. Neither a clear preview nor a lack of warnings proves production fit or accessibility compliance. See previews.md for the model and safety limits.

## Finish the editorial workflow
See [Editorial review and export](editorial_review.md) for creating manual revisions, editing AI candidates, previewing, confirming behavior, recording four review states and notes, handling stale drafts, and downloading Markdown/CSV/JSON reports or approved replacements.

## Edit source records
Open Edit an existing source record below the catalog. Choose Source record to edit, change source text/context/metadata, and Save source changes. The ID and extension metadata remain; originals on disk do not change. Invalid edits leave the catalog untouched. Existing affected review drafts stay visible as stale and cannot contribute approved replacements until explicitly rebased and reviewed. This is separate from revising candidate copy.

For a clean demonstration, use a new private browser session; avoid restarting the running app if you need its current session. Download reports before ending the session. See portfolio_demo.md for the complete v1 walkthrough.
