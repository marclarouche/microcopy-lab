# Microcopy Lab — Milestone 4 completion

Implemented October 15, 2026 in `/Users/cyberlifecoach/Projects/microcopy-lab`.
Application **0.4.0**, preview engine **preview-1.0**, record schema **1.0**, editorial guide **1.1**.

Milestone 4 is complete. Milestone 5 has not started. The refreshed app is running at http://127.0.0.1:8501. The URL was opened through the system browser outside Codex as requested. Restarting the app clears its temporary catalog; reload test files to begin the guided test.

## Delivered previews

Five fixed templates cover button/action area, form field/label, tooltip/helper, error/warning, and onboarding/empty state. Each can display exact original copy and a current candidate in side-by-side, original-only, or revised-only views. Controls include compact/comfortable/wide frames and light/dark themes. The helper template uses native expand/collapse; simulated buttons and fields are disabled.

Character usage uses exact Unicode code-point counts and the source override or guide limit. Separate advisory line estimates flag possible clipping/wrapping in the selected layout. Full original/revised text remains available even when a template clips long content. Punctuation, whitespace and tokens remain unchanged.

Current AI candidates are passed to previews only when the existing input fingerprint matches. Five offline human-authored example pairs are distinctly labeled illustrative, pending, and not AI output or approval. Repeated example loads do not duplicate records, and an illustrative pair is withheld when its source ID exists with different source data.

The preview recomputes token integrity rather than trusting a candidate's protected_tokens_valid flag. Foreign-source, blank or token-invalid candidates are withheld. Overlength candidates remain inspectable with warnings because previewing is not acceptance. No source text or revision status is changed.

## Architecture and files

- `src/microcopy_lab/preview_models.py`: pure typed snapshots, character/token metrics, advisory fit estimates and bounded fixture validation. No Streamlit, IO, network or AI calls.
- `ui/preview_panel.py` and `ui/__init__.py`: scoped fixed markup, escaped text, comparison controls and presentation-only sample reading.
- `app.py`: hands only current AI revisions to the preview panel. Optional AI presentation returns safely so invalid AI settings cannot suppress offline previews.
- `samples/fleetops_preview_examples.json`: five paired fictional component examples.
- `tests/test_previews.py`: 83 new regression cases.
- `schemas/preview_comparison.schema.json` and `schemas/preview_example.schema.json`: API/fixture contracts.
- Updated README, architecture/security/user guide, local AI notes, development log and new `docs/previews.md`.
- Package metadata/local editable installation updated to 0.4.0; mypy now checks the UI helpers as well as the core/app. No new runtime dependency was added.

Earlier samples, milestone records, PRDs and GitHub reference were preserved. No Git commit or push was performed.

## Actual verification

- **226 tests passed in 5.50 seconds** in the installed Python 3.12 environment: all 143 previous cases plus 83 preview cases.
- **Ruff lint and format checks passed.**
- **Strict mypy passed:** no issues in 17 source files.
- **Final pip-audit:** no known dependency vulnerabilities found. The unpublished local microcopy-lab 0.4.0 package is skipped by the advisory service; its code is covered locally.
- The refreshed localhost service started successfully and its health endpoint was checked.
- Real browser verification on the staged release showed the original/revised button comparison and confirmed helper disclosure collapse. A screenshot is included among the outputs. The temporary browser tab and verification server were closed afterward.

Regression tests cover all five templates and both themes, original/revised toggles, character/Unicode/line estimates, explicit source limits, fit-versus-length separation, protected tokens, forged token flags, candidate/source mismatch, hostile scripts/markup/CSS/URLs in every template, literal-text preservation, no network/AI preview calls, bounded fixture validation, provenance, repeated loads, stale AI, source collisions, filters, and invalid optional AI settings.

## Guided user test kit

The user-facing kit is also copied to `samples/guided_test/`:

- `START-HERE.md`: project name, full product context, every manual-entry field/value, and step-by-step expected behavior.
- `01-guided-catalog.csv` and `.json`: the same nine cases, with all required/optional source fields.
- `02-validation-errors.csv`: intentionally invalid rows plus a valid control.
- `03-malformed.json`: intentionally broken input for atomic failure testing.

Verified outcomes with guide 1.1:

- Either good catalog imports **9 accepted / 0 rejected**, with **1 length warning**.
- Deterministic audit produces **7 findings across 6 strings**.
- After the good catalog is loaded, the validation file imports **1 accepted / 5 rejected**.
- The malformed file is safely rejected with nothing imported.

The kit covers implemented normal workflows and common failures, not every automated edge case or later approval/export functionality. The CSV and JSON alternatives should not both be imported for the initial test. The walkthrough explains which files to upload and how to exercise AI and all five previews.

## Security and limits

Text is HTML-escaped before insertion into fixed text nodes. Imported/generated values never populate CSS, attributes, IDs, URLs or executable templates. Static scoped styles use enum-selected layouts/themes. Streamlit's sanitized st.html renderer is used with JavaScript disabled; unsafe_allow_html and raw iframe HTML are not used. Templates include no remote assets, links, scripts or product actions.

Layout estimates assume display-cell widths and template padding; they do not measure actual browser/font glyphs. Responsive columns can shrink frames, and emoji/scripts/zoom can change fit. A lack of warnings does not establish production fit, correct behavior, keyboard support, accessible names or accessibility compliance.

State remains in memory. Approval workflows, final approved-copy/audit exports, persistent projects and automatic product modifications remain outside this milestone. Existing local AI safeguards continue unchanged. Process decisions and evidence are retained in `docs/development_log.md` for the requested later software-process explanation.
