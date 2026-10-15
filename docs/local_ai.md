# Local Ollama review — Milestone 3

## Setup and use
Ollama runs as a separate trusted local service. Microcopy Lab does not install models, start the service, execute shell commands, or download anything. If you need to provision a model, use Ollama's own installation and model-management workflow before running the app.

The default endpoint is `http://127.0.0.1:11434`. Only numeric loopback HTTP endpoints with explicit ports are accepted; DNS names, remote addresses, credentials, paths, queries, fragments, HTTPS/cloud endpoints, and cloud-labelled model names are rejected. The model must appear in local tags with GGUF weight metadata; show metadata must confirm local parameters and no remote model/host.

Ollama can offer cloud models even through its local daemon. This app rejects cloud/remote metadata, but trusts the local daemon to describe its models honestly. For defense in depth, configure the daemon itself for local-only operation using Ollama's documented `OLLAMA_NO_CLOUD=1` or `disable_ollama_cloud` setting, then restart it yourself. The app does not change global daemon settings or interrupt other projects.

`config/ai.yaml` controls the endpoint, default model, timeouts, run record cap, byte bounds, output tokens and context size. The UI model field can select another installed model. Start with a single string on CPU. A timed-out record does not erase the source catalog or deterministic findings; reduce the batch/model/output size or adjust timeout within the validated cap.

Use Load AI examples, select AI-DEMO-001, then Run local AI review. Do not assume every string needs a rewrite. AI-DEMO-003/006 intentionally omit verified behavior and should lead to questions when behavior is needed. Original FleetOps strings also omit that evidence. Example behaviors are fictional human-authored facts, not evidence about a real product.

## Request and output boundaries
Each inference request reviews one source string; a run contains at most the configured selection cap. The system message is application-owned. All source/context/notes/behavior fields are serialized into a separate user data message. Only defined context fields are included; arbitrary source extension fields and source-reference URLs are not added to prompts. The model gets no tools, images, browsing, files, or prior conversation.

POST `/api/chat` uses `stream: false`, a Pydantic-generated JSON schema in `format`, temperature zero, seed zero, and bounded context/output options. GET `/api/tags` and POST `/api/show` check installed model identity before text inference. There is no pull endpoint, redirect handling, environment proxy routing, cloud fallback, or automatic retry. Byte bounds apply before requests and while reading responses. Socket timeouts and a run deadline bound work; the deadline prevents remaining requests after exhaustion. This is not a hard real-time guarantee against a malicious local daemon or slow header delivery.

Response JSON rejects duplicate keys and nonfinite constants. The daemon envelope must indicate a complete assistant response for the selected model, without tool calls. Truncated output is rejected. Strict output models reject unsupported categories, extra fields, forged review statuses, oversized findings, malformed JSON, and foreign source IDs. One failed record does not discard valid records from the same run.

Model findings cover clarity, terminology, tone, actionability, accessibility-related wording, jargon, error recovery, and instructions. Rule IDs and source/finding/revision identifiers are assigned by the application. Each accepted candidate records model identity, a source evidence quote, rationale, category/severity, a finding link, pending review status, and behavior-confirmation requirement. Identical candidate texts are displayed once per source while retaining all findings. The run records model digest, app/prompt/guide versions, selection, input fingerprint, counts, and per-record statuses.

## Candidate validation
The model cannot claim that a candidate is approved or technically safe. The application enforces:

1. Nonblank human-supplied `product_behavior`, an exact evidence quote at least eight characters long, and a rationale.
2. Source/default character limits and a genuine text change.
3. Exact dynamic-token multiset integrity, including declared custom tokens and absent-source metadata checks.
4. Exact protected product-name spelling/counts and configured terminology/prohibited-phrase constraints.
5. Candidate vocabulary grounded in source, quoted evidence, allowed grammatical connectors, and applicable preferred terminology.
6. Preservation of explicit source numbers and negation markers; negative quoted evidence cannot support an unqualified positive candidate.

These are conservative lexical checks, not a semantic verifier. They can reject useful paraphrases and can miss meaning changes using allowed words. Every accepted candidate still requires human behavior confirmation. Missing evidence produces clarification instead of a fabricated recovery/action claim. Invalid candidates are withheld with safe diagnostics and clarification questions. Findings remain advisory; model explanations/questions are untrusted plain text.

## Status and limitations
A source result is completed, needs_clarification, partial (some candidates withheld), or failed. A run is completed, partial, or failed; completed means the requested analysis finished, not that copy is approved. Counts distinguish analyzed sources, failures, partial outcomes, and questions. A clear string may produce no findings. Missing behavior triggers a clarification question even if the model omits one.

Fingerprints bind output to catalog, guide, AI settings, selected IDs, and prompt version. Changes hide stale AI results until rerun. Imported source records are never modified. The UI provides analysis tables/questions and simulated previews. Milestone 5 retains candidates as separate editorial drafts with versioned human decisions and exports; initial AI tables remain the original pending analysis output. No persistent database or automatic source replacement is implemented. See editorial_review.md.

Temperature/seed settings improve repeatability but do not guarantee identical AI responses. Mocked tests are reproducible; live model tests are smoke checks, not measured editorial accuracy. No UX quality score or accessibility compliance claim is made.

## API sources
The adapter follows Ollama's official [chat endpoint](https://docs.ollama.com/api/chat), [structured output guidance](https://docs.ollama.com/capabilities/structured-outputs), [model listing endpoint](https://docs.ollama.com/api/tags), and [local/cloud configuration FAQ](https://docs.ollama.com/faq). These sources describe transport behavior, not a guarantee that generated wording is correct.
