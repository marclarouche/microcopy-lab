# Microcopy Lab v1.0 release validation

Release date: October 15, 2026. Scope: local prototype on the existing macOS/Python 3.12 environment. These are observed checks, not universal guarantees. Source release version: 1.0.0.

## Executed evidence

- Full pytest regression and acceptance suite: **283 passed**. Final measured duration is recorded in milestone_6_completion.md.
- Ruff lint and formatting: passed. Strict mypy covers engine, app, UI and the offline demo script.
- `pip check`: no broken requirements. `pip-audit`: no known dependency vulnerabilities; unpublished local microcopy-lab 1.0.0 cannot be queried in PyPI advisory data and was explicitly skipped. No application runtime dependency was added for release.
- Editable local v1.0.0 package metadata installed successfully using pip's isolated setuptools build.
- Both the offline scripted report and final live-AI report validate against schemas/editorial_report.schema.json.
- The verified external runtime/development package versions are captured in requirements-verified.txt. This is not a hash-locked or cross-platform tested build.

## Offline and unavailable-model behavior

Release tests patch socket connections and DNS to fail if attempted, then execute both scripts/run_demo.py and an AppTest review/preview/export session. Both complete with zero network attempts. The scripted fictional session produces nine sources, seven deterministic findings, four revision states and one approved replacement.

A separate test makes the real Ollama HTTP adapter's connection fail. It records a safe failed-AI outcome and still allows manual approval and report generation. The code's fixed numeric-loopback endpoint, no-proxy/no-redirect behavior and schema/source limits are separately tested. No machine-wide network or Ollama setting was changed for these tests.

This validates exercised paths after dependencies/assets are installed. It is not an air-gapped installation test, a hardware network capture, or a guarantee about third-party daemon internals.

## Final live local inference smoke

One bounded two-record run completed in **157.25 seconds** using installed **qwen3-vl:4b-instruct**, digest **ee4b975b58c17ce268cd19d40db35d5edc64603035d2ffc1fee1968eb0947f7b**.

| Source | Outcome | Findings | Candidates | Clarification questions |
| --- | --- | --- | --- | --- |
| AI-DEMO-001 (Proceed, with supplied fictional behavior) | completed | 3 | 1 pending: Submit Report | 0 |
| AI-DEMO-003 (Error 42, without verified behavior) | needs_clarification | 3 | 0 | 3 |

No failed or partial records were reported. The candidate's token validation passed. Source data was fictional; no model was downloaded and no cloud model was used. The elapsed time describes this two-record smoke run, not a latency guarantee, benchmark or broad model-accuracy evaluation. Model outputs can vary.

## Browser smoke and downloads

A separate temporary localhost server on port 8502 and a hidden browser session loaded the five paired preview fixtures, adopted them as pending illustrative drafts, confirmed the fictional behavior, approved PREVIEW-001, and compared Proceed with Submit report. The summary showed five sources, four pending drafts and one approved draft.

The real Download approved replacements CSV action produced a file. Parsing it verified exactly one PREVIEW-001 row with approved_text Submit report, status approved and source/revision traceability. Screenshots in docs/images show the actual preview and summary. The temporary browser and server were closed; the existing user's port 8501 process/session was not restarted or cleared.

## Regression and security scope

Coverage includes malformed/oversized inputs, duplicate IDs, Unicode/extension metadata, literal terms, placeholder counts, hostile markup/instructions, unsupported AI output and claims, all five previews, live model-generation compatibility, source edits and invalid-edit rollback, decision version resets, stale snapshots, conflicting/forged approvals, safe CSV prefixes (including control/Unicode whitespace), escaped Markdown, exact JSON, report schema, failed/partial processing summaries and engine/presentation import boundaries.

CSV catalog rows now retain finding_details even when no revision exists. Source snapshots must match the current catalog as well as their stored fingerprint before a decision can count as current. Approval cannot establish semantic truth; the human confirmation requirement remains visible.

## Limits and unresolved risks

No known failing automated check remains at release. This was not a penetration test, comprehensive browser/device matrix, accessibility certification or real-user usability study. Only the existing development environment was exercised. Python 3.13/3.14, other operating systems, different model/hardware combinations, all spreadsheet applications and every possible input remain unverified.

There is no database, durable save/reopen format, authentication, production source integration, automatic replacement/publication or cloud deployment. Reports contain imported content/notes intentionally; download them before ending the session. Dependency advisory results can change after this date. Trust the local computer and Ollama daemon.

During release work the docs folder disappeared unexpectedly. The user confirmed the deletion was unintended and requested restoration. Saved milestone documents/completion artifacts were restored, the current review/release updates were reapplied, and documentation presence was checked before the initial commit. No executable source was lost; the cause of the disappearance was not established.
