# v1 acceptance evidence

This matrix maps every PRD acceptance criterion to executed evidence. It records functional scope, not a guarantee for every possible input, platform, model, or assistive technology.

| Criterion | Implementation and evidence |
| --- | --- |
| AC-001 Import CSV/JSON | test_foundation.py validates required fields, UTF-8, duplicates, malformed and oversized inputs, partial rows, metadata and both 40-row sample formats. Guided nine-row catalogs reproduce seven findings. |
| AC-002 Manual add/edit | test_ui_manual_and_filter adds a source; test_release.py checks validated source editing in core and UI, invalid edits preserving the catalog, immutable IDs/extensions, and approval staleness/rebase. |
| AC-003 Rule checks | test_audit.py verifies literal terminology, configurable categories, length, punctuation, generic labels, consistency and exact human-authored 40-row expectations (15 findings, 3 length violations). |
| AC-004 Token protection | test_audit.py, test_ai.py, test_previews.py and test_review_exports.py reject missing/added/renamed/duplicated tokens, missing declarations and forged validity flags across inference, previews, approval and export. |
| AC-005 Structured AI | Mocked strict-output tests plus the final live qwen3-vl:4b-instruct two-record run. AI-DEMO-001 returned 3 findings and one pending token-valid candidate, Submit Report. |
| AC-006 Missing behavior | Mocked tests and final live AI-DEMO-003 outcome: needs_clarification, 3 questions, zero revisions. Filters mitigate unsupported claims but do not prove factual entailment. |
| AC-007 Five previews | All five templates, layouts, light/dark themes, original/revised/side-by-side modes and exact content are exercised in test_previews.py. Actual browser QA confirms the release button comparison. |
| AC-008 Inert markup | Malicious markup tests across all templates; fixed HTML templates with escaping and sanitized st.html; Markdown exports escape source HTML/image/link syntax. Source URLs are not followed. |
| AC-009 Review decisions | test_review_exports.py exercises pending, approved, rejected, needs_clarification, notes and explicit behavior confirmation, including UI flows and blocked token approval. |
| AC-010 Approval resets | Text/rationale edits increment the version and reset approval/confirmation. Notes-only edits preserve it. Source/context/style changes make decisions stale; release UI tests verify explicit rebase to pending. |
| AC-011 Accurate exports | JSON/CSV/Markdown source IDs, metadata, versions, model attribution, original/proposed/approved separation, full-catalog counts and unapproved exclusion are parsed/asserted. Actual browser-approved CSV download was read and verified as one PREVIEW-001 / Submit report / approved row. |
| AC-012 No Ollama | Release test simulates socket failure for the real adapter, verifies a failed AI record and successful manual approval/export. Offline UI review, preview and four download controls also execute with connections/DNS forbidden. |
| AC-013 No source-driven execution/network | Endpoint/redirect/proxy tests, inert hostile inputs, fixed templates and AST boundary checks. Core offline demo and UI complete with socket.connect and DNS blocked and zero attempts. Local Ollama remains an explicitly trusted dependency. |
| AC-014 Offline after setup | Network-forbidden demo and UI tests prove those exercised runtime paths make no connection attempts. Installed local AI uses loopback; final live smoke confirms the installed model works. Dependency installation/advisory scanning require separate Internet access. |
| AC-015 Automated checks | Final results are recorded in release_validation.md. Earlier test failures and corrections are recorded in development_log.md rather than hidden. |
| AC-016 Independent engine | AST checks reject Streamlit/subprocess/eval/exec in the core; scripts/run_demo.py imports only core APIs and runs without Streamlit or inference. Strict mypy checks typed public APIs. |

All P0 features F-001 through F-015 are covered by the above workflows and repository instructions: local UI, input metadata, style/rules/tokens, optional bounded local AI, five previews, explicit review, reports, traceability and tests. F-015 uses the validated local YAML configuration; guide changes require rerun and invalidate affected decisions. P1 tone-profile switching was not required for release and remains outside v1. Filtering/dashboard and light/dark previews are present.

The review forms do not establish accessibility compliance or product meaning. Browser coverage is a desktop smoke test, not comprehensive cross-browser/device or assistive-technology testing. There is no persistent project store or cloud deployment.
