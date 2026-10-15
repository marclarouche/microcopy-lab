# Reproducible v1 demonstration

Use a new private browser session for the demonstration so your working project is untouched. Open http://127.0.0.1:8501 after launching from the repository root.

## Short browser walkthrough

1. Name the project **FleetOps — Portfolio Demo**. Set product context to **Fictional fleet maintenance interface. Draft reports are submitted for supervisor review; product meaning must be verified before approving copy.**
2. Upload **samples/guided_test/01-guided-catalog.csv**, click **Import file**, then **Run deterministic audit**. Expect nine accepted sources, one length warning, and seven deterministic findings. Explain why a rule match is advisory.
3. Open **Create a manual revision**, choose **TEST-001**, enter **Submit report**, and use rationale **Names the verified submission action.** Select **Create pending revision**.
4. In **Component previews**, choose TEST-001 and its review draft. Compare Proceed with Submit report, character usage and frame estimates. Explain that disabled controls illustrate wording rather than submit an actual report.
5. Return to Editorial review. Verify the fictional product behavior, enter a review note, check behavior confirmation, choose approved, and save. Download the approved replacements CSV. The source text remains Proceed; only the separate replacement mapping contains the accepted wording.
6. Change the replacement to **Submit draft** and save. The version increments and returns to pending with behavior confirmation cleared. This demonstrates why an approval belongs to particular wording.
7. Optional source-edit check: open **Edit an existing source record**, choose TEST-001, change its context, and save. The retained draft becomes stale. Rebase explicitly before reviewing it again. A source edit affects only the session catalog, not the imported file on disk.
8. For all five component types, choose **Load preview examples**, then use Preview string PREVIEW-001 through PREVIEW-005. The helper disclosure is interactive; layouts and light/dark themes are illustrative.
9. Optional local AI: review only TEST-001, then TEST-008. Candidates depend on the installed model; missing verified behavior should produce clarification rather than invented recovery steps. This part requires installed Ollama/local weights and can take minutes. It is separate from the reproducible offline demo.

Download JSON, CSV and Markdown reports before closing the session. Explain the deliberate CSV formula-safety prefix and exact-text JSON alternative.

## Scripted offline artifacts

```sh
.venv/bin/python scripts/run_demo.py --output work/demo-output
```

Expected: nine sources; seven deterministic findings; four scripted fictional drafts, one each pending/approved/rejected/needs_clarification; exactly one approved replacement. Outputs: review.json, catalog.csv, review.md, approved.csv. Revision/project IDs and generation timestamps vary; editorial content and counts are fixed. The script has no access to the browser session and never invokes Ollama.

## Evaluation boundaries

Keep human-authored fixtures, scripted decisions and actual model output separately labeled. The sample is not a usability study, production fleet application or accessibility certification. Refer to acceptance_matrix.md and release_validation.md for executed evidence and coverage limits.
