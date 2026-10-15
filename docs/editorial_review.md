# Editorial review and export — Milestone 5

Import your catalog and run an audit. AI review is optional. Findings identify concerns; a revision is a separate proposed replacement, and approval belongs to a specific revision version.

## Complete a review

1. Scroll to **Editorial review**. Valid current AI candidates are automatically copied here as pending drafts, with their source, model, rationale, and evidence retained. Changing the AI selection or model does not delete drafts.
2. If the AI gave only findings, open **Create a manual revision**, choose **Revision source**, enter **New replacement text** and **Revision rationale**, and select **Create pending revision**. This also works completely offline without Ollama.
3. Choose **Revision to review**. Read the original, context, and verified product behavior. Edit **Replacement text**, **Rationale**, and **Review notes** as needed. Select **Save revision and decision** to save an edit. A material text/rationale edit increments the version, resets it to pending, clears the old evidence quote from the current version, and clears behavior confirmation—even if Approved was selected in that save. The initial candidate remains in the JSON/Markdown report, and edited_by_human identifies subsequent human edits.
4. Scroll to **Component previews** and choose the matching **Preview string** and **Preview candidate**. Inspect the comparison, characters, tokens, and layout warnings. Previewing does not approve the draft.
5. Return to the review form. Verify product meaning using actual requirements or a product owner. Check **I verified that this replacement preserves product behavior**, choose **approved**, and select **Save revision and decision**. Mechanical approval checks enforce nonblank copy, character limits, exact placeholder counts/spelling, protected product names, and current source/context/style settings. These checks cannot establish semantic correctness.
6. Alternatively choose **rejected**, **needs_clarification**, or **pending**, add notes, and save. Those states do not require behavior confirmation. Notes-only changes do not increment the version or invalidate an existing approval.
7. Only one revision per source can be approved. Set an earlier approval to another status before approving an alternative.
8. Under **Review summary and exports**, download reports and approved replacements before ending the session.

The illustrative preview fixture remains separate. **Load preview examples** loads the sources and comparison pairs; rerun/scroll to Editorial review and select **Add illustrative examples to review** to bring their candidates into the workflow. They start pending with origin illustrative, no model identity, and no behavior confirmation.

## Stale drafts

Each entry stores its exact source snapshot and a fingerprint of project ID, product context, full source metadata, and the complete style guide. Changes to those values make the entry stale. Existing drafts and notes remain visible; stale approvals cannot enter approved exports. Select **Rebase draft on current source** to attach the retained draft to current data as a new pending version, then verify and review it again. Adding unrelated catalog records or changing a project display name does not invalidate an existing decision. Model settings identify the candidate's origin, rather than invalidating a retained human draft.

## Downloads

- **Download JSON report**: exact Unicode source data and unknown metadata, full active style guide, app/version/time/fingerprint, fresh deterministic findings, current AI run including questions/diagnostics/model details, review entries with source snapshots, initial candidates, current versions/notes/status, summary, warnings, limitations, and a separate approved_replacements list.
- **Download CSV catalog**: one row per source/revision; sources with no revisions have an unreviewed row. Original IDs/text, proposed text, approved text, notes/status/version, rule/category/severity/model/origin, JSON source metadata and limitations are separate columns. Multiple alternatives produce multiple rows. This is a review report, not the input importer schema.
- **Download Markdown report**: readable project/summary/source/findings/review information and current AI processing details. Source markup and Markdown link/image syntax are escaped.
- **Download approved replacements CSV**: only current approved versions, with original text, approved_text, original source ID, revision ID/version, review traceability and metadata. No automatic source-file rewrite or publication occurs.

CSV prefixes formula-like cells (=, +, -, @ after leading whitespace, and leading tab/newline) with an apostrophe to reduce spreadsheet formula execution. Use JSON for exact text preservation. Reports may contain the full imported catalog and editorial notes; the app creates them in memory and downloads them only when selected. They are not a persistent project save/reopen format.

Summary counts cover the full catalog and a fresh deterministic audit, independent of display filters. AI failed/partial counts refer to the current matching run only; drafts from previous runs retain candidate provenance, but are not a complete AI run history. Pending/approved/rejected/needs-clarification counts describe revision decisions, separately from advisory finding rows. There is no aggregate UX score or accessibility certification. CSV finding_details also retains source-linked findings for strings without revision drafts. JSON session_id equals project_id for this single-project in-memory session.

## Boundaries

Source records stay unchanged. Review decisions do not automatically resolve findings or imply product behavior is correct. Sessions remain in memory, without accounts, database, durable history, report reimport, or automatic product changes. Version 1.0 release evidence is documented in release_validation.md and acceptance_matrix.md.
