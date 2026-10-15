# Milestone 5 completion — editorial review and export

Implemented version 0.5.0 after explicit user authorization on October 15, 2026.

## Delivered
- `src/microcopy_lab/review.py`: source/context/style-bound review entries; initial candidate provenance; manual/AI/illustrative origins; editable replacement/rationale; four decisions; notes; explicit behavior confirmation; material-edit version resets; stale-source rebasing; one approval per source; independent token, protected-term and length checks.
- `src/microcopy_lab/exporters.py`: full JSON report, CSV review catalog, Markdown editorial report and approved-only CSV. Fresh full-catalog deterministic audit, accurate revision-state summary, category/severity counts, length warnings and current failed/partial AI record counts. Original metadata/IDs, model identity, notes, versions and limitations remain traceable.
- `ui/review_panel.py` and `app.py`: manual draft creation, AI candidate retention, explicit illustrative sample adoption, review forms and download controls. No inference is needed for manual review or exports. Initial AI analysis tables are distinct from subsequent editorial decisions.
- `ui/preview_panel.py`: retained current review drafts are previewable and actual review status is shown. Stale drafts are withheld until explicitly rebased; illustrative comparisons remain labeled separately.
- `ai_models.py` / `ai_engine.py`: an independent source/guide fingerprint lets the export engine reject stale AI run snapshots without relying only on UI filtering.
- `schemas/review_entry.schema.json`, updated AI result schema; README, architecture, security, preview, local AI and user documentation; dedicated `docs/editorial_review.md` walkthrough.
- `tests/test_review_exports.py`: 37 new parameterized test cases, including complete offline manual create/approve/preview/edit workflow; reset approval/confirmation after edits; notes-only decisions; rejection/clarification; token/length/product-name checks; stale source/context/config; conflicting/forged approvals; exact Unicode/metadata JSON; CSV formulas; inert Markdown; unapproved export exclusion; current partial AI outcomes and candidate provenance. Existing preview tests were updated for retained review drafts while continuing to verify stale analysis exclusion and changed-source withholding.

## Verification
- Full pytest suite: 266 passed in 8.28 seconds.
- Ruff lint: passed; format check: 48 files already formatted.
- Strict mypy: no issues in 20 source files.
- pip-audit: no known dependency vulnerabilities. Local unpublished microcopy-lab 0.5.0 was explicitly skipped by the advisory service.
- Local health endpoint: OK at http://127.0.0.1:8501/_stcore/health. Existing app process/session was not restarted or cleared.
- Editable package metadata installed successfully as 0.5.0. The initial no-build-isolation attempt failed because setuptools was absent in the runtime environment; standard isolated editable installation succeeded. No application dependency was added.
- No fresh live Ollama inference was needed: candidate-generation behavior is unchanged; review/export integration used deterministic mocked AI results and offline manual sessions.

## Decisions and limits
Approval applies to a particular candidate version and explicit source/context/configuration snapshot. Notes-only edits preserve it; text/rationale edits reset both decision and behavior confirmation. An AI candidate edited by a human retains the initial model candidate while marking the current version as human-edited. Initial AI finding statuses remain separate from editorial revision decisions; approving a candidate does not silently mark advisory findings resolved.

The full JSON report preserves exact source fields/extension metadata; CSV intentionally apostrophe-prefixes formula-like cells, and Markdown escapes source markup/link syntax. Approved-only CSV is a replacement mapping with review/source metadata, not a rewritten original input file. Imports, outputs, generated copy and notes are inert data.

All state remains in memory; reports are downloads, not save/reopen project files. No persistent approval history, accounts, database, source application changes, automatic publication, accessibility certification or proof of semantic equivalence is provided. Human review remains required. Milestone 6 release QA and portfolio work were not started.
