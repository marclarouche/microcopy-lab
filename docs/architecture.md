# Architecture
`app.py` is presentation only: widgets, temporary project state, audit triggering, and filtered tables. All processing belongs to `src/microcopy_lab`, with no Streamlit imports or session-state dependencies.

- `models.py`: versioned source, project, validation, finding, revision, token-integrity, audit-result, and summary contracts.
- `config.py`: bounded SafeLoader YAML with typed editorial settings, complete positive component limits, allowed categories/syntaxes, and terminology conflict validation.
- `importers.py`: bounded UTF-8 CSV/JSON import, required-field validation, duplicate IDs, row diagnostics, metadata preservation, and initial length warnings.
- `placeholders.py`: fixed-syntax token discovery, literal custom tokens, and occurrence-count comparison for candidate text.
- `terminology.py`: literal whole-phrase matching, protected spans, and canonical comparison without modifying sources.
- `rules.py`: pure per-string checks and structured rule evidence.
- `engine.py`: deterministic orchestration, cross-string consistency checks, stable findings, input fingerprints, and count summaries.

Audits call no filesystem or network API. YAML reading and file import are explicit boundaries. Inputs and configuration are never changed by an audit. Findings remain separate from source records and carry deterministic UUID5 IDs derived from project ID, source ID/text, rule, evidence, and engine version. Output order is stable by source and rule. Input fingerprints include the full project, guide, application version, and engine version, preventing stale UI results after edits or configuration changes. Fingerprints are cache invalidation data, not anonymization guarantees.

The deterministic engine audits every validated string or raises a safe validation error for unsupported project limits/duplicate identifiers; it does not report partial success. Import errors remain separate from audit findings. UI summary counts refer to the whole catalog, while table filters affect only visible rows. There is no global quality score.

The token-integrity helper now gates local AI candidate suggestions. Milestone 5 review state management and exporters consume these independent records. All state remains in memory and can be reused through a future native interface. Dependency ranges remain constrained, without a frozen lockfile.

## Milestone 3 adapter and orchestration
`ai_config.py` owns validated local-only inference settings. `ai_models.py` defines strict untrusted response contracts and typed per-record/run outcomes. `ai_adapter.py` uses standard-library HTTP with fixed endpoints, explicit local-model checks, bounded JSON, sanitized typed errors and an injectable transport for tests. No new runtime dependency was added.

`ai_engine.py` constructs separated system/data messages, orchestrates a small explicit selection, validates source IDs, records partial failures/clarification, and preserves source/config inputs. `revisions.py` gates candidates using the existing token/terminology engine plus exact behavior evidence and conservative vocabulary/polarity/number checks. The UI owns only controls, result state, tables and stale-result display.

Deterministic analysis remains pure and works independently when Ollama is absent or AI fails. Network activity is confined to the explicit local Ollama adapter; source URLs are never fetched. AI remains untrusted and cannot assign accepted review status or overwrite original records. The run records the selected model/digest, prompt, application and guide versions. See local_ai.md for request/validation policy and residual limitations.

## Milestone 4 preview boundary
`preview_models.py` computes immutable source-linked original/revised snapshots, exact character usage, token counts and advisory line budgets without IO or Streamlit. `ui/preview_panel.py` renders escaped text in five fixed, scoped templates with sanitized st.html and JavaScript disabled. Presentation helpers live outside the src engine; type checking includes the ui package.

The existing optional AI section returns only current revisions to the preview panel. Separating it from main means invalid AI settings cannot suppress offline previews. Human-authored paired examples are kept in separate session state, never inserted into AI results or presented as approval. Full source equality prevents illustrative source-ID collisions from receiving the wrong candidate. The preview rechecks token integrity independently of provenance flags. The preview itself never changes a source or decision. Milestone 5 passes retained current review drafts to this panel, and the separate review form owns versioned edits and decisions.

## Milestone 5 review and reporting boundary
`review.py` owns source-bound review entries, initial candidate provenance, version increments, explicit decisions, approval guards and rebasing. All updates return validated copies and leave original source records unchanged. `exporters.py` builds in-memory reports with a fresh deterministic audit, matching AI snapshot, source/guide/version traceability and independently rechecked approved replacements. `ui/review_panel.py` owns Streamlit forms and download controls. No core module imports Streamlit. JSON retains exact data; CSV neutralizes formulas, and Markdown escapes source markup/links. Stored Pydantic objects cross live-reload boundaries through validated JSON to retain session compatibility. No new dependency, database, model invocation or external network call is needed for editorial review or export.

## v1 release source editing
`catalog.py` applies only supported field changes to a validated copy of a source record and project. IDs/extensions stay unchanged; source edits do not implicitly rebase decisions. `ui/source_panel.py` owns the explicit edit form. Audit/AI snapshots and validation summaries are serialized/revalidated across live-reload model generations. Reports independently verify retained source snapshots as well as fingerprints. `scripts/run_demo.py` orchestrates existing core APIs for a separate fictional session. Release requirements and measured checks are mapped in acceptance_matrix.md and release_validation.md.
