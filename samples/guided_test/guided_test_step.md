# Microcopy Lab: a short guided test

Everything here is fictional. This kit exercises v1 input, analysis and previews. For source editing, editorial decisions and final exports, continue with docs/editorial_review.md and docs/portfolio_demo.md in the repository. Persistent project save/reopen is not implemented.

## 1. Project fields
Open the app in your external browser at http://127.0.0.1:8501. Start with a fresh session for the counts below.

**Project name — paste this:**

FleetOps — Guided Test

**Product context — paste this:**

FleetOps is a fictional fleet-maintenance app for dispatchers. Users name vehicles, filter maintenance reports, submit draft reports for supervisor review, and track work. Submitting does not publish or delete a report. A failed save leaves the current draft available. No automatic retry or network-recovery behavior has been verified. All data in this test is fictional.

## 2. Upload the good catalog
Upload **01-guided-catalog.csv**, then select **Import file**. Alternatively use **01-guided-catalog.json**; it contains the same nine cases. Choose only one format for the initial import. CSV uses blank optional cells where JSON uses null.

Expected: **9 accepted, 0 rejected**, with **1 character-limit warning**. The catalog preserves all required and optional source fields, including context, goal, behavior, design notes, tokens, screen/product area, and source reference. Source URLs are fictional references and are never followed. schema_version 1.0 is the record format version, not a quality score or software milestone.

Select **Run deterministic audit**. Expected: **7 findings across 6 strings**, including **1 length violation**.

| ID | What it demonstrates | Deterministic expectation |
| --- | --- | --- |
| TEST-001 | Button: Proceed | Generic component wording |
| TEST-002 | Long vehicle label | Character limit |
| TEST-003 | Tooltip: Utilize… | Preferred terminology: use |
| TEST-004 | Error with `{report_id}` | No configured match; token retained |
| TEST-005 | Empty state: No stuff yet | Generic component wording |
| TEST-006 | Clear Cancel button | No configured match |
| TEST-007 | Embedded script/instructions | Inert literal text; no configured match |
| TEST-008 | Unexplained Error 0x8004 | Code-only error |
| TEST-009 | Outer spaces and !! | Whitespace + repeated punctuation |

Filter component types, finding categories and severities. Summary counts describe the whole audited project, while table filters change visible rows. A missing finding does not certify good writing or security.

## 3. Try the five visual previews
Clear the component filter before trying all five types. The nine uploaded strings cover all five types. In **Component previews**, choose TEST-001, TEST-002, TEST-003, TEST-004, and TEST-005 to inspect each original template.

Then select **Load preview examples**. This adds five separate PREVIEW-… records with clearly labeled human-authored comparison candidates; these are not AI output or approved replacements. Use the Preview string selector to try:

| Preview ID | Component |
| --- | --- |
| PREVIEW-001 | Button and action area |
| PREVIEW-002 | Form field and label |
| PREVIEW-003 | Tooltip/helper text; expand/collapse About this field |
| PREVIEW-004 | Error/warning with `{report_id}` preserved |
| PREVIEW-005 | Onboarding/empty-state panel |

Toggle Side by side / Original / Revised, frame size, and light/dark theme. Check character usage and layout warnings. Full text remains available below each component even when the illustrative layout clips it. Controls are inert; these are approximate layouts, not production fit or accessibility verification.

For an independent test of the count expectations in other sections, do this preview-example step last: it adds five records and may add its own audit findings.

## 4. Run a small AI review
Ollama must already be running locally. Keep **qwen3-vl:4b-instruct** in Installed Ollama model, or choose another supported model already installed. Check local Ollama models if necessary.

First select only **TEST-001** under Strings for local AI review, then Run local AI review. The source includes explicit fictional behavior evidence. A model may suggest wording such as Submit report; output wording and finding counts can vary. Candidates stay pending, are never applied, and must pass evidence, token, terminology and fit checks. Inspect the current AI candidate in Component previews.

Next review only **TEST-008**. Its behavior/cause/recovery is deliberately unknown. Expected behavior: clarification questions instead of invented recovery instructions, and no accepted replacement candidate.

Optionally review **TEST-004** to inspect `{report_id}` preservation. You may also try TEST-006: clear text may receive no findings or no useful change.

Start with one string. On this machine, local CPU smoke tests took about 51–71 seconds; this is not a latency guarantee. A timeout or withheld candidate is reported safely and does not damage the catalog. Change selection/model or project context after a run and observe stale-result protection. Rerun to refresh results. Preview changes do not themselves run Ollama.

## 5. Fill every manual-entry field
Use the following exact values in Manual string entry. Protected tokens is deliberately empty; do not paste the word “empty.”

| App field | Value |
| --- | --- |
| String identifier | MANUAL-001 |
| Component type | button |
| Original text | Go |
| User or interface context | Primary action on the draft maintenance report screen. |
| Screen identifier | REPORTS |
| Product area | Fleet maintenance |
| User goal | Submit a maintenance report for review. |
| Verified product behavior | Submit report sends the current maintenance report for supervisor review. It does not publish or delete the report. |
| Design notes | Fictional manual test. Confirm product behavior before using a suggestion. |
| Source reference | fictional://guided-test/manual-001 |
| Protected tokens | Leave empty |
| Character limit | 24 |

Select Add string. Expected: **1 accepted, 0 rejected**. A fresh deterministic audit adds a generic-button finding for Go. Manual entry/import clears prior result snapshots; original sources remain unchanged.

## 6. Check validation and failed imports
These counts assume the initial nine-row catalog has already been imported. Preview examples/manual entry may also be present; they do not change these batch outcomes.

1. Upload the initial good catalog again. Expected: **0 accepted, 9 duplicates rejected**. Existing records survive.
2. Upload **02-validation-errors.csv**. Expected: **1 accepted (VALID-CONTROL), 5 rejected**: one duplicate TEST-001, missing context, unsupported component, invalid identifier containing a space, and a zero character limit. The file is structurally valid, so the one valid row is retained. Upload it only once for these counts.
3. Upload **03-malformed.json**. Expected: a safe malformed-input diagnostic, **nothing imported**, and the existing catalog preserved. It is intentionally broken; do not repair it before this test.
4. Select TEST-007 in the preview. The `<script>…</script>` and instructions must display literally; they must not run or fetch the URL.

Do not upload START-HERE.md. The malformed file is only for the intentional failure step. The built-in paired preview fixture is loaded by its button rather than uploaded as a catalog.

## Reset and limits
Session data is temporary. A new private/incognito browser session provides a clean test; restarting the app also resets session state. Keep these source files. A table’s built-in Download as CSV downloads that table only. Use Review summary and exports for full Markdown/CSV/JSON reports and approved replacements. Normal operations are local; there is no automatic source-application change or persistent project save/reopen. Source records can be explicitly edited in memory, and revisions can be approved separately.

This kit covers implemented workflows and common failures; the automated suite also covers oversized inputs and deeper edge cases.

Verified with the bundled guide 1.1. Both good formats accepted nine records with the same seven deterministic findings, and the validation file accepted one/rejected five after the good catalog was loaded.
