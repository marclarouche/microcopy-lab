# Microcopy Lab — Milestone 1 completion

Implemented October 15, 2026 in `/Users/cyberlifecoach/Projects/microcopy-lab`.
The literal `/Projects` directory does not exist. The existing user project folder contained the supplied PRD; its setup instructions also specify `~/Projects/microcopy-lab`.

Milestone 1 is complete. Milestone 2 has not started.

## Delivered files
Paths below are relative to the project directory.

- `pyproject.toml`, `.gitignore`, `AGENTS.md`, `README.md`
- `.streamlit/config.toml`
- `app.py`
- `src/microcopy_lab/__init__.py`
- `src/microcopy_lab/models.py`
- `src/microcopy_lab/config.py`
- `src/microcopy_lab/importers.py`
- `config/ux_style_guide.yaml`
- `samples/fleetops_strings.csv`, `samples/fleetops_strings.json`
- `samples/expected_findings.md`
- `schemas/ui_string.schema.json`, `schemas/catalog.schema.json`
- `tests/test_foundation.py`
- `docs/PRD.md` (copy of the existing PRD)
- `docs/architecture.md`, `docs/security.md`, `docs/user_guide.md`, `docs/input_schema.md`
- `docs/milestone_1_completion.md` (this report)

The original `microcopy-lab-prd.md` and `github.md` were preserved. Git was initialized; no commit or remote was created. A project-local `.venv` was installed using Python 3.12.14 and is ignored by Git.

## Architecture and behavior
The independent `src/microcopy_lab` package owns domain models, configuration loading, parsing, validation, duplicate detection, and length diagnostics. No core module imports Streamlit or reads session state. `app.py` owns only presentation and temporary project state.

Pydantic records include explicit schema version 1.0 and stable stored identifiers. The source catalog is separate from foundational finding and revision contracts. Those contracts do not implement later workflows.

The UI provides project name/context, CSV and JSON upload, a fictional 40-string FleetOps demo, manual entry including optional context metadata, a catalog table, component filters, and validation summaries. Imports retain source IDs, whitespace, tokens, and unknown metadata. Invalid rows are skipped; malformed files and resource-limit failures reject the batch without replacing existing records. Character-limit violations preserve the text and produce warnings.

## Installation and launch
The local environment is already installed. Launch now:

```sh
cd /Users/cyberlifecoach/Projects/microcopy-lab
source .venv/bin/activate
python -m streamlit run app.py --server.address 127.0.0.1
```

For a fresh installation using an available Python 3.12 executable:

```sh
cd /Users/cyberlifecoach/Projects/microcopy-lab
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
python -m streamlit run app.py --server.address 127.0.0.1
```

The shell's default Python was 3.15, so development used the available bundled Python 3.12 runtime. Activating the installed `.venv` selects the correct interpreter. Open http://127.0.0.1:8501 after launching. The verification server was stopped after its health check.

## Actual verification

- Final tests in the installed project environment: **36 passed in 21.86 seconds**, Python 3.12.14. Command: `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q -p no:cacheprovider`.
- Ruff check: **all checks passed**.
- Ruff format check: **passed**.
- Strict mypy: **no issues in 5 source files** (engine plus app).
- Final `pip-audit` in the project environment: **no known vulnerabilities found**. The unpublished local `microcopy-lab` package is skipped because it is not on PyPI; its code is covered by local checks.
- Real Streamlit startup: **HTTP 200** from its localhost health endpoint; server log confirmed binding to **127.0.0.1**. Server terminated cleanly after verification.
- Streamlit AppTest exercised demo loading, duplicate demo loading, manual hostile-text entry, and component filtering without application exceptions.

Tests cover Pydantic model validation, required fields, both import formats, duplicate IDs including existing catalogs, UTF-8/BOM, multiline CSV, malformed input, input/field/record limits, character counting, source metadata, inert markup, unsafe YAML rejection, and separation of the engine from Streamlit.

Initial verification found a 3-second UI startup timeout and one type error; both were corrected. The first dependency scan found vulnerabilities in the venv's bootstrap pip 25.0.1. Pip was upgraded to 26.2.1 in both validation and project environments; the final project audit passed. No vulnerability was suppressed.

## Limitations and security
Project state is temporary memory: no saving, export, source editing workflow, AI, contextual analysis, previews, review workflow, persistent database, authentication, or cloud services. Dependencies use constrained version ranges rather than a frozen lockfile. No accessibility compliance or production text-fit claims are made.

Default uploads are limited to 5 MiB; the YAML record cap defaults to 1,000. Invalid files receive safe generic diagnostics without source text or parser internals. Length counts Unicode code points rather than grapheme clusters or pixels. Some very large CSV cells may be rejected by Python's parser. CSV unknown metadata stays text; JSON metadata preserves JSON types.

The localhost configuration disables Streamlit usage telemetry and user-visible stack traces. Imported text is never executed, interpreted as HTML, used to modify configuration, or followed as a URL. YAML uses SafeLoader with size bounds and model validation. The engine has no network code and application code does not log source strings. Dependency installation and advisory scans require network access; ordinary app operation is local. Do not expose this unauthenticated prototype to a network.

## Milestone 2 readiness
The import, configuration, versioned models, and test suite provide a foundation for deterministic terminology checks, component rules, structured findings, and placeholder validation. Editorial settings are present, but only input character-limit diagnostics are applied in Milestone 1. Source tokens are preserved; revision integrity checking remains future work. Proceed only on a separate instruction for Milestone 2.
