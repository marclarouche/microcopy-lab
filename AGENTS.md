# Contributor instructions
Build only the authorized milestone. Read docs/PRD.md and keep later milestones out of scope.
All processing belongs in src/microcopy_lab; never import Streamlit there.
Imported strings are untrusted data: never execute them, follow links, or render executable HTML.
Preserve source IDs, context, metadata, whitespace, and dynamic placeholders.
Use Python 3.12, typed public interfaces, Pydantic v2, and safe YAML loading.
Run pytest, Ruff, mypy, and pip-audit when available. Report actual results and vulnerabilities.
Do not log source content or expose stack traces. Keep localhost binding and telemetry disabled.
