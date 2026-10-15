# Microcopy Lab — v1.0
Local-first interface content catalog with deterministic audits, optional local Ollama review, simulated UI previews, human editorial decisions, and Markdown/CSV/JSON exports. Import, inspect, filter, manually enter strings, and run advisory rule checks. FleetOps Demo is entirely fictional.

## Install and launch
Use Python 3.12 from the repository root:
```sh
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
python -m streamlit run app.py --server.address 127.0.0.1
```
Open http://127.0.0.1:8501. The repository's `.streamlit/config.toml` disables usage telemetry, limits uploads to 5 MB, and hides stack traces. Launch from this directory so those settings apply.

## Supported input
UTF-8 CSV (header required) and JSON (top-level array). A UTF-8 BOM is accepted.
Required fields: `string_id`, `component_type`, `original_text`, `context`.
Components: `button`, `field_label`, `tooltip`, `error_warning`, `onboarding_empty_state`.
Optional fields: `schema_version` (1.0), `screen_id`, `product_area`, `user_goal`, `max_chars`, `product_behavior`, `design_notes`, `protected_tokens`, `source_reference`.
`max_chars` is a positive integer (CSV accepts blank for default); `protected_tokens` is a list of nonblank literal strings, encoded as JSON inside a CSV cell (up to 1,000 declarations, 200 code points each). Unknown fields survive as metadata. CSV metadata stays text; JSON metadata retains JSON types. IDs are case-sensitive, 1–200 characters, and cannot contain whitespace or control characters.
See `docs/input_schema.md`, `schemas/ui_string.schema.json`, and both sample catalogs.

A malformed file is rejected atomically. Structurally valid files can import valid rows while reporting invalid or duplicate rows. Existing project records always survive failed imports. The configurable record limit defaults to 1,000 and counts existing records plus submitted rows. The 5 MB limit uses 5 × 1024 × 1024 bytes. Length uses Python Unicode code points, not visual width or grapheme clusters. Overlength copy stays available with a warning.

## Deterministic audit
Load the FleetOps Demo, then select **Run deterministic audit**. The bundled guide produces 15 findings across 15 of the 40 strings, including three character-limit violations. Filter findings by category, severity, and the catalog's component selection. Source text and metadata remain unchanged.

Checks cover preferred terminology, prohibited phrases, character limits, edge whitespace, repeated question/exclamation marks, configured generic component wording, code-only errors, absent declared tokens, and related terminology variants. Rule matches require editorial judgment; they do not prove a defect or accessibility compliance. Findings have stable source-linked IDs, explicit rule IDs, offsets where applicable, and a guide/engine version. Catalog or configuration changes invalidate displayed results until the audit runs again.

The YAML guide enables categories and sets literal terms, protected product names, component wording, character limits, and supported placeholder syntaxes. No configuration regex or imported instructions execute. See `docs/methodology.md` for rule semantics and limitations.

## Engine use
```python
from pathlib import Path
from microcopy_lab.config import load_style_guide
from microcopy_lab.engine import audit_project
from microcopy_lab.importers import import_catalog
from microcopy_lab.models import Project
from microcopy_lab.placeholders import validate_placeholder_integrity

guide = load_style_guide(Path("config/ux_style_guide.yaml"))
result = import_catalog(Path("samples/fleetops_strings.json").read_bytes(), "json", guide=guide)
project = Project(name="FleetOps", strings=result.strings)
audit = audit_project(project, guide)
print(audit.summary)
# Independent callers can check token integrity explicitly.
check = validate_placeholder_integrity(
    project.strings[24], "Delete {count} work orders?", syntaxes=guide.placeholder_syntaxes
)
assert check.valid
```

## Checks
```sh
python -m pytest
python -m ruff check .
python -m ruff format --check .
python -m mypy
python -m pip_audit
```
Dependency installation and vulnerability scanning can require Internet access; normal application operation uses no external services.

## Local AI review
Ollama is optional: deterministic audits work without it. Install/start Ollama separately and install a local model before use. The app never downloads models or starts/stops the daemon. `config/ai.yaml` selects a model and inference bounds; the UI can select another installed model name.

1. Select **Check local Ollama models** to inspect availability.
2. Select **Load AI examples** for six fictional strings, including explicit behavior evidence, missing context, clear text, dynamic tokens, and hostile input.
3. Select one source ID under **Strings for local AI review** (start with AI-DEMO-001).
4. Select **Run local AI review**. Read per-record status, findings, pending candidates, clarification questions, and safe diagnostics.

The original 40-string demo lacks verified behavior descriptions. It may receive clarification questions rather than replacement copy. A nonblank `product_behavior` field supplies the human-authored evidence required for candidates. Suggestions are never applied or approved automatically.

AI settings default to a numeric loopback endpoint, installed `qwen3-vl:4b-instruct`, 120 seconds per inference, a 180-second run budget, at most five selected strings, 32 KiB request/128 KiB response bounds, a 512-token output cap, and an 8,192-token context. CPU inference may be slow; begin with one string. Limits are configurable within validated hard caps. No retries run automatically; record failures remain explicit.

The adapter requires local GGUF/parameter metadata and rejects cloud-labelled/remote-backed models. It ignores environment HTTP proxies, does not follow redirects, and exposes only fixed tags/show/chat endpoints. Run the trusted Ollama daemon in local-only mode as described in `docs/local_ai.md`.

## Component previews
Select a catalog source under **Component previews**. Its component type chooses one of five fixed templates: button/action area, field/label, tooltip/helper, error/warning, or onboarding/empty state.

Select **Load preview examples** for five human-authored comparison pairs without running Ollama. These start explicitly illustrative, pending and unapproved; use Add illustrative examples to review to make editorial decisions. Current validated AI candidates are also available for the matching source; stale AI runs are excluded. No candidate means an original-only preview.

Toggle **Side by side / Original / Revised**, **compact / comfortable / wide** frames, and **light / dark** themes. Review character usage, layout warnings, protected token counts and full literal text. The helper template supports native expand/collapse. All displayed controls are illustrative; buttons/fields perform no product action.

Source and candidate text are HTML-escaped into fixed scoped templates and passed through Streamlit's sanitized HTML display with JavaScript disabled. Imported markup stays text. Token-invalid or foreign-source candidates are withheld even if their metadata claims validation. Overlength candidates can be viewed with warnings; previewing is not acceptance. Layout estimates use display-cell widths rather than font/pixel measurement, and narrow browser columns can shrink the selected frame. This does not prove production fit or accessibility compliance. See `docs/previews.md`.

## Known limitations
All project data is in session memory and can be lost when the session ends. Download reports before ending a session. There is no persistent project save/reopen or automatic product modification. Component checks use a finite configured vocabulary; terminology matching is literal without stemming. AI filters cannot prove semantic entailment or perfect injection resistance, so candidates start pending and require explicit human behavior confirmation before approval.

Built-in token formats are `{name}`, `${name}`, `%s`, `%d`, and `%f`; `%%` is escaped. Other formats require explicit literal declarations. Integrity protects spelling/counts, not semantic token order. Preview templates are approximate and cannot verify behavior, browser/font/device fit, accessible names, keyboard behavior, or accessibility compliance.

All six planned v1 milestones are implemented. See `docs/acceptance_matrix.md` for requirements evidence, `docs/release_validation.md` for measured release checks, and `docs/portfolio_case_study.md` for the portfolio narrative. See `docs/previews.md`, `docs/local_ai.md`, and `docs/development_log.md`.

## Editorial decisions and downloads
AI candidates become pending review drafts. You can also create a manual revision for any source without AI. Edit and save the draft, inspect it in Component previews, then confirm verified behavior and choose pending, approved, rejected, or needs_clarification. Material edits reset approval and confirmation; notes-only updates retain the decision. Only one current version per source can be approved. Source/context/style changes make prior decisions stale until explicitly rebased and reviewed again.

Download the JSON report (lossless source/metadata), CSV catalog, Markdown report, or approved replacements CSV. Reports contain version/source/model traceability, statuses, notes, limitations and a fresh deterministic summary. CSV formula-like values are apostrophe-prefixed; JSON preserves exact text. Reports do not automatically rewrite input files or modify your product. See `docs/editorial_review.md` for the complete walkthrough and export semantics.

## Edit an existing source
Open **Edit an existing source record** below the catalog. Select a record, edit supported fields, and save. The ID and unknown metadata stay unchanged. Invalid edits preserve the catalog; accepted edits affect session data only, clear prior analysis, and make affected review decisions stale until explicitly rebased/reviewed. Editing a source and editing a proposed replacement are separate actions.

## Reproduce the release
The supported development target is Python 3.12. `requirements-verified.txt` pins the external runtime/development packages from the verified environment; it is an environment snapshot, not a platform-independent or hash-locked build. After creating/activating a Python 3.12 virtual environment, use:

```sh
python -m pip install -r requirements-verified.txt
python -m pip install --no-deps -e .
python -m pip check
python scripts/run_demo.py --output work/demo-output
```

The scripted demo is fictional and offline: nine sources, seven findings, four review states and one approved replacement. Generated IDs/timestamps vary. Normal review/export requires no network; installed local AI communicates only with loopback. Installation and dependency auditing may use Internet access. Python 3.13/3.14 and other operating systems were not release-tested. See `docs/portfolio_demo.md` for the browser walkthrough.
