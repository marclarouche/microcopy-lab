# Microcopy Lab — Milestone 2 completion

Implemented October 15, 2026 in `/Users/cyberlifecoach/Projects/microcopy-lab`.
Application version: **0.2.0**. Deterministic engine: **deterministic-1.0**. Bundled editorial guide: **1.1**. Domain schema: **1.0**.

Milestone 2 is complete. Milestone 3 has not started.

## Delivered behavior

- Preferred terminology and prohibited-phrase checks using literal, case-insensitive whole-phrase matching.
- Configured character limits, edge whitespace, repeated question/exclamation marks, generic component wording, and code-only error checks.
- Related terminology variants within the same screen and component, with explicit related source identifiers and behavior-confirmation flags.
- Protection of recognized placeholders and configured product/API names from editorial matching.
- A candidate-token validation API that detects removed, renamed, case-changed, duplicated, or newly introduced supported tokens. Declared tokens absent from original source are reported as metadata findings and invalidate candidate checks.
- Structured, source-linked findings with deterministic IDs, rule IDs, severity, evidence offsets where relevant, and guide/engine traceability.
- Count summaries and UI filters by category, severity, and component. Whole-project summaries remain independent of table filters.
- Input fingerprints that hide stale results after project or guide changes. Successful imports that add records clear prior audits.
- Configurable categories, component labels, terminology, prohibited phrases, protected names, supported placeholder syntaxes, limits, and record cap.

The bundled FleetOps catalog produces **15 findings across 15 of 40 strings**, including **three character-limit violations**. The acceptance fixture is human-authored; it does not derive its expectations from the implementation.

Original source text, metadata, identifiers, context, and configuration are unchanged by audits. All findings are advisory and require editorial judgment. No source replacements, AI calls, or product modifications occur.

## Architecture and files

New engine modules:

- `src/microcopy_lab/engine.py`: orchestration, stable findings, fingerprints, summaries.
- `src/microcopy_lab/rules.py`: independently testable per-string rules.
- `src/microcopy_lab/terminology.py`: phrase matching, protected spans, canonical comparison.
- `src/microcopy_lab/placeholders.py`: token discovery and candidate integrity checks.

Updated `models.py` adds audit results, summaries, and token-validation contracts, while retaining separate original/finding/revision records. Updated `config.py` validates the new guide settings and rejects ambiguous terminology mappings. All core modules remain independent of Streamlit and session state.

Additional changes:

- `app.py`: audit action, findings table, counts, filters, and stale-result protection.
- `config/ux_style_guide.yaml`: guide 1.1 and demonstration rules.
- `tests/test_audit.py`: 37 new acceptance/regression cases; all 36 foundation cases remain.
- `samples/expected_findings.json`: exact deterministic acceptance expectations.
- `samples/expected_findings.md`: separates current deterministic expectations from future contextual observations.
- `schemas/audit_result.schema.json`, `schemas/token_validation.schema.json`, `schemas/style_guide.schema.json`, and updated UI string schema.
- Updated README, architecture, security, input schema, and user guide.
- New `docs/methodology.md`: rule catalog, configuration semantics, matching boundaries, and limitations.
- `pyproject.toml` and package version updated to 0.2.0; the project-local editable installation was refreshed.

Your updated `github.md`, original PRD, and Milestone 1 report were preserved. No Git commit or push was performed.

## Actual verification

- **73 pytest cases passed** in the installed Python 3.12 project environment.
- **Ruff lint passed** and **format check passed**.
- **Strict mypy passed:** no issues in nine source files, including the UI.
- **pip-audit: no known vulnerabilities found** in the updated environment. The local unpublished `microcopy-lab` 0.2.0 package is skipped because it is not on PyPI; its code is covered by local checks.
- **Real Streamlit startup passed:** localhost health endpoint returned HTTP 200, the server log confirmed binding to 127.0.0.1, and the test server stopped cleanly.
- Streamlit tests exercised demo import, duplicate handling, manual hostile-text entry, catalog filtering, audit execution, category/severity filters, and stale-result invalidation.

Tests also verify deterministic IDs/order, source/config immutability, Unicode length boundaries, phrase matching and protected spans, configuration rejection/defaults, candidate token multisets, explicit-token bounds, custom token prefixes, whitespace inside custom tokens, consistency grouping, empty projects, record limits, expected demo findings, and absence of audit network/command execution.

## Launch and checks

The installed environment is ready:

```sh
cd /Users/cyberlifecoach/Projects/microcopy-lab
source .venv/bin/activate
python -m streamlit run app.py --server.address 127.0.0.1
```

Open http://127.0.0.1:8501, load FleetOps Demo, then select **Run deterministic audit**. The verification server was stopped after testing.

For a fresh installation, use Python 3.12 to create `.venv`, then run:

```sh
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
python -m pytest
python -m ruff check .
python -m ruff format --check .
python -m mypy
python -m pip_audit
```

## Limits, security, and next milestone

State remains in memory. There is no saving/export, approval workflow, revision editor, Ollama adapter, contextual AI analysis, dynamic preview, database, authentication, or cloud integration.

Matching is literal without stemming or semantic inference. Component rules recognize a configured vocabulary; errors with meaningful prose are not automatically diagnosed. Same-screen terminology comparisons require human confirmation. An unmatched string is not proof of UX quality or accessibility compliance. Length counts Unicode code points, not visual width.

Built-in placeholders support `{name}`, `${name}`, `%s`, `%d`, and `%f`; `%%` is escaped. Names use ASCII letters/underscores followed by letters/digits/underscores/dots. Other formats, including double-brace templates, ICU, and positional/width printf, require explicit literal declarations. Candidate validation preserves spelling and counts but allows reordering and cannot verify meaning. Future revision callers must enforce its `valid` result before accepting text.

Imported strings remain inert plain text. Configuration phrases and custom tokens are regex-escaped literals; placeholder syntax selectors choose fixed application patterns. Upload, record, field, configuration, and token bounds remain enforced. Application code adds no telemetry, network calls, logging of source text, or automatic modification path. Keep the unauthenticated app bound to localhost.

The independent engine, versioned results, and token-integrity helper are ready for a separately authorized Milestone 3 Ollama adapter and structured contextual suggestions. No Milestone 3 work was started.
