# Microcopy Lab — Milestone 3 completion

Implemented October 15, 2026 in `/Users/cyberlifecoach/Projects/microcopy-lab`.
Application: **0.3.0**. Contextual prompt: **contextual-1.0**. Style guide: **1.1**. Domain schemas: **1.0**.

Milestone 3 is complete. Milestone 4 has not started. The app is running at http://127.0.0.1:8501 after a release refresh; its temporary session catalog needs reloading.

## What was added

- An optional local Ollama adapter with installed-model discovery, local-weight metadata checks, fixed tags/show/chat endpoints, structured schema output, typed sanitized errors, and bounded input/output/time/record limits.
- Contextual findings for clarity, terminology, tone, actionability, accessibility-related wording, jargon, error recovery, and instructions.
- Pending source-linked candidate revisions with rationale, exact behavior evidence, category, severity, rule ID, model identity, and mandatory behavior-confirmation status.
- Candidate gates for missing behavior evidence, exact evidence quotes, character fit, token multisets, protected product names, terminology/prohibited phrases, grounded vocabulary, explicit numbers, negation and restrictive qualifiers.
- Clarification questions instead of unsupported action/recovery assertions. Malformed, truncated, foreign-source, tool-call, or forged-status output is rejected. Unsupported candidates are withheld with safe diagnostics.
- Per-record outcomes and whole-run counts that preserve valid results when other records fail or the run budget is exhausted.
- Stale-result invalidation for changes to source data, guide, model/settings, selection, or prompt version.
- Streamlit controls for checking local models, loading AI examples, selecting a small batch, running review, and inspecting findings, questions, pending candidates and diagnostics.
- Six fictional AI examples with explicit behavior evidence, missing context, clear text, dynamic tokens and hostile source content.
- API schemas, setup/security documentation, and a development decision/evidence log for the user's later full process explanation.

Original source text, IDs, context and metadata are never changed by AI review. Identical candidate texts are coalesced per source while retaining all findings. No candidate is automatically applied or approved.

## Architecture and files

New core modules:

- `src/microcopy_lab/ai_config.py`: validated local-only settings.
- `src/microcopy_lab/ai_models.py`: strict untrusted response contracts and typed record/run results.
- `src/microcopy_lab/ai_adapter.py`: standard-library loopback HTTP, model checks, response/schema validation and injectable test transport.
- `src/microcopy_lab/ai_engine.py`: separated prompts/data, bounded per-source orchestration, traceability, clarification and partial failure handling.
- `src/microcopy_lab/revisions.py`: application-owned candidate validation using the existing deterministic engine.

Updated `models.py` makes revision traceability explicit. `app.py` owns only controls, session state and plain tables/text. Core modules have no Streamlit/session-state dependencies. No new runtime package was required.

Other files include `config/ai.yaml`, `samples/fleetops_ai_examples.json`, `tests/test_ai.py`, AI/revision schemas, updated README/architecture/security/methodology/user guide, and new `docs/local_ai.md` and `docs/development_log.md`. Package metadata and the local editable installation are now 0.3.0. Earlier PRDs, milestone reports, sample catalogs and your GitHub reference were preserved. No commit or push was performed.

## Actual verification

- **143 tests passed in 3.24 seconds** in the installed Python 3.12 project environment, including all 73 earlier cases and 70 new AI cases.
- **Ruff lint passed; format check passed.**
- **Strict mypy passed:** no issues in 14 source files including the UI.
- **Final pip-audit:** no known dependency vulnerabilities found. The unpublished local `microcopy-lab` 0.3.0 package is skipped because it is not on PyPI; its code is checked locally.
- **Refreshed localhost service:** health endpoint returned HTTP 200, and the server log confirmed binding to 127.0.0.1:8501.

Offline tests use mocked responses and require neither Ollama nor Internet access. They cover valid findings/candidates, schema enforcement, foreign IDs, forged status fields, missing evidence, token changes, protected names, polarity/numbers/qualifiers, candidate deduplication, invalid endpoints/cloud metadata, byte/record/time limits, redirects, unavailable models, partial results, deterministic fallback, prompt/data isolation, and UI execution/staleness.

Live smoke checks used the already-installed **qwen3-vl:4b-instruct** model, digest `ee4b975b58c17ce268cd19d40db35d5edc64603035d2ffc1fee1968eb0947f7b`, on Ollama 0.40.4. Ollama reported CPU-only inference.

1. The initial fictional button request reached its original 60-second timeout. The client returned a safe timeout diagnostic without losing source records or deterministic functionality.
2. A retry with a bounded 120-second timeout and 512-token output cap completed in **50.91 seconds**. It produced evidence-backed “Submit Report” candidates, pending human confirmation. The model repeated identical text under several findings; release code coalesces such duplicates, covered by a regression test.
3. A fictional “Error 42” request without product behavior evidence completed in **70.97 seconds** with **three clarification questions and zero revisions**. The application did not invent recovery steps.

These are individual smoke-test measurements, not general latency or editorial-accuracy guarantees. No additional model was downloaded, and no global daemon setting was changed.

## Try it now

Open http://127.0.0.1:8501 and refresh the page if needed.

1. Select **Load AI examples**.
2. Under **Strings for local AI review**, select **AI-DEMO-001**.
3. Keep `qwen3-vl:4b-instruct` as the installed model.
4. Select **Run local AI review**.
5. Inspect findings and pending candidates; confirm product behavior before using any wording.

Start with one string on this CPU runtime. AI-DEMO-003 intentionally lacks verified behavior and demonstrates clarification. The original 40-string FleetOps demo also lacks explicit `product_behavior`, so it can produce questions rather than replacement copy.

To launch later:

```sh
cd /Users/cyberlifecoach/Projects/microcopy-lab
source .venv/bin/activate
python -m streamlit run app.py --server.address 127.0.0.1
```

Ollama must already be running with an installed supported local model. The app never downloads models or starts/stops the daemon. Current settings are 120 seconds per inference, 180 seconds per run, five selected records, 32 KiB request/128 KiB response bounds, 512 output tokens, and an 8,192-token context. Multiple CPU requests may exceed the run budget; remaining failures are explicit. Configure limits in `config/ai.yaml` within its validated caps.

## Security, limits and readiness

Only numeric loopback HTTP endpoints are accepted. The adapter ignores environment proxies, does not follow redirects, rejects cloud-labelled/remote-backed model metadata, and provides no tool, URL-fetching, file, shell, model-pull or product-modification path. The local Ollama daemon remains trusted to report its weights honestly; daemon-level local-only mode is recommended in `docs/local_ai.md`. Source URLs are never followed.

System instructions are separate from serialized untrusted source data. Strict responses and application-owned IDs/statuses prevent model text from becoming approval actions or executable instructions. AI findings/questions remain plain text. Application code does not log prompts, source text or model output by default. The trusted daemon may retain its own prompt/model cache.

Evidence/vocabulary/polarity checks are conservative lexical filters. They may reject useful paraphrases and cannot prove semantic entailment, factual correctness, or perfect injection resistance. Every surviving candidate remains pending and requires human behavior confirmation. Token checks preserve recognized spelling/counts, not semantic order. Built-ins remain `{name}`, `${name}`, `%s`, `%d`, `%f`; other formats require explicit literals. No quality score, accessibility certification or production text-fit guarantee is claimed.

State is temporary memory. Simulated component previews, approval controls, final report exports, persistent storage, cloud services and automatic source modifications remain out of scope. The typed findings/revisions and independent engine are ready for separately authorized Milestone 4 previews.

The what/how/why decisions and actual evidence are preserved in `docs/development_log.md` and the three milestone completion reports for the complete software-process explanation when you request it.
