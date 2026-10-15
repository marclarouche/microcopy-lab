# Milestone 6 completion — v1.0 release

Completed October 15, 2026 following explicit user authorization. The source/package version is 1.0.0.

## Release work

- Mapped all 16 PRD acceptance criteria and P0 requirements to executable or observed evidence in acceptance_matrix.md.
- Closed the missing AC-002 existing-source edit requirement with pure catalog.edit_source and a separate UI form. IDs/extensions are preserved, invalid edits are atomic, files on disk stay unchanged, and affected review drafts become stale until explicit rebase/review.
- Added final release tests for source editing, selector isolation, stale/forged source snapshots, offline demo/UI with connections and DNS forbidden, actual local-adapter unavailability with continued approval/export, control/Unicode whitespace formula prefixes, source findings in CSV without revisions, published report schema and architecture/security boundaries.
- Strengthened report checks to compare retained source snapshots as well as fingerprints. CSV now includes finding_details; token validity is recomputed directly. Retained audit/AI/validation records are revalidated across live-reload class generations.
- Added scripts/run_demo.py: a separate fictional offline project with nine strings, seven deterministic findings, all four review states and one approved replacement, producing JSON/CSV/Markdown and approved-only CSV.
- Published the editorial report JSON schema, refreshed model schemas, and captured the verified external package environment in requirements-verified.txt.
- Updated installation, usage, architecture, security, guided test kit and review documentation. Added portfolio_case_study.md, portfolio_demo.md, release_validation.md and actual browser screenshots under docs/images.

## Executed checks

- **283 tests passed in 10.66 seconds.**
- Ruff lint passed; formatting check passed (56 files).
- Strict mypy passed across 23 source files, including the demo script.
- pip check: no broken requirements.
- pip-audit: no known dependency vulnerabilities. Unpublished local microcopy-lab 1.0.0 was explicitly skipped because it is not on PyPI.
- Local editable v1.0.0 installed successfully; no runtime dependency was added.
- Offline demonstration and UI tests completed with socket.connect and DNS forbidden and zero attempts. The unavailable-local-adapter test still completed manual review/export.
- Actual browser QA on isolated localhost port 8502 approved a fictional fixture and downloaded an approved CSV; parsing confirmed one PREVIEW-001 / Submit report / approved row. Real screenshots were captured. Temporary browser/server closed; the user's existing port 8501 process/session remained intact.
- Final local Ollama run: 157.25 seconds total for two records, qwen3-vl:4b-instruct digest ee4b975b58c17ce268cd19d40db35d5edc64603035d2ffc1fee1968eb0947f7b. The evidence-backed button produced 3 findings and 1 pending candidate, Submit Report. Error 42 without behavior evidence produced 3 questions and zero revisions. No failed/partial records, model download or cloud call.
- Offline demo and live AI JSON reports validated against the published editorial report schema.
- A pattern scan found no matching private-key/GitHub/OpenAI-style credential strings in release source. This is a limited sanity check, not proof that every possible secret format is absent.

## Corrections during release

Adding the source editor exposed a positional audit-button regression; the test now selects Run deterministic audit by label. Strict typing of the newly included demo script required an explicit ReviewEntry list annotation. The docs folder disappeared during QA; the user confirmed this was unintentional and authorized restoration. Saved milestone documentation and completion reports were restored and review/release updates reapplied. The cause of that disappearance was not established; executable source was not lost.

## Release scope and limitations

All six planned v1 milestones are implemented and the mapped acceptance checks pass in the tested local environment. This is a session-based prototype with explicit human approval and downloaded reports. It is not a cloud deployment, persistent project store, source-application integration, automatic publication tool, usability study or accessibility certification. Only the current macOS/Python 3.12 setup and bounded installed-model examples were exercised; broader device/OS/browser/assistive-technology coverage and model accuracy remain unmeasured. See release_validation.md for precise boundaries.

Initial Git commit/push is performed separately after these release artifacts and checks are complete, as requested by the user. No force push is needed because the destination repository has no remote refs.
