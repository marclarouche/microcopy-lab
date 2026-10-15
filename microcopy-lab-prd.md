# Microcopy Lab
## Product Requirements Document (PRD)

**Version:** 1.0  
**Date:** October 15, 2026  
**Status:** Implementation baseline  
**Product:** AI UX Writing & Interface Content Assistant  
**Architecture:** Local-first, modular Python application  
**Interface:** Streamlit  
**AI Runtime:** Ollama  
**Development Budget:** $0–$20 target, excluding hardware and labor

---

# 1. Executive Summary

Microcopy Lab is a local-first AI-assisted UX writing application that helps technical writers, UX writers, product designers, and content specialists evaluate and improve interface text.

The application analyzes labels, buttons, tooltips, error messages, warnings, success messages, empty states, and onboarding instructions.

It combines deterministic editorial rules with local AI analysis to identify potential problems with clarity, consistency, tone, actionability, accessibility-related wording, and character length.

Users can review suggested revisions, preview them in simulated interface components, and export approved recommendations.

Microcopy Lab does not automatically modify source applications, publish content, or certify accessibility compliance.

**Its fundamental purpose is to improve interface communication while preserving verified product meaning and human editorial authority.**

# 2. Problem Statement

Software interfaces frequently contain short pieces of text that have a significant influence on usability.

Examples include ambiguous buttons, technical error codes without explanations, inconsistent labels, warnings that omit consequences, and onboarding instructions that assume users already understand a process.

Technical writers and UX writers must evaluate these strings in context, maintain consistent terminology, and collaborate with product and engineering teams to verify intended behavior.

Conventional proofreading tools may identify spelling and grammar problems but typically lack the product context needed to evaluate whether an interface instruction is useful.

Microcopy Lab will provide a structured review process that connects each string to its component, user intent, editorial rules, and available product requirements.

# 3. Product Objectives

The application shall:

1. Import and organize UI text strings.
2. Classify strings by interface component type.
3. Evaluate terminology consistency and configured writing rules.
4. Identify potentially ambiguous, unclear, or unhelpful wording.
5. Flag accessibility-related writing concerns for human review.
6. Generate contextual AI revision suggestions.
7. Preserve product behavior and technical meaning.
8. Preview original and revised copy in simulated components.
9. Support explicit editorial review decisions.
10. Export structured reports and approved replacement strings.
11. Operate locally without cloud AI services.
12. Demonstrate UX writing and documentation governance skills.

# 4. Target Users

## 4.1 UX Writer

Reviews labels, calls to action, errors, helper text, and onboarding content.

## 4.2 Technical Writer

Maintains terminology consistency between product interfaces, technical manuals, and online help.

## 4.3 Content Designer

Uses consistent voice, tone, and component-specific language across a software product.

## 4.4 Product Designer

Evaluates copy alternatives in representative interface layouts.

## 4.5 Portfolio Reviewer

Evaluates the author's knowledge of usability, editorial decision-making, AI-assisted workflows, and application architecture.

# 5. Scope

## 5.1 Included in Version 1

| ID | Feature | Priority |
|---|---|---|
| F-001 | Local Streamlit application | P0 |
| F-002 | Manual UI string entry | P0 |
| F-003 | CSV and JSON import | P0 |
| F-004 | Structured component metadata | P0 |
| F-005 | Terminology and style checks | P0 |
| F-006 | Character-length validation | P0 |
| F-007 | Placeholder and token protection | P0 |
| F-008 | Local Ollama analysis | P0 |
| F-009 | Contextual revision suggestions | P0 |
| F-010 | Five interactive component previews | P0 |
| F-011 | Human review workflow | P0 |
| F-012 | Markdown, CSV, and JSON export | P0 |
| F-013 | Source and revision traceability | P0 |
| F-014 | Automated functional and security tests | P0 |
| F-015 | Configurable YAML style guide | P0 |
| F-016 | Findings filters and dashboard | P1 |
| F-017 | Alternative tone profiles | P1 |
| F-018 | Light and dark preview themes | P1 |

P0 features are required for v1 completion. P1 features are desirable but must not delay release.

## 5.2 Excluded from Version 1

* Figma API integration.
* Direct Figma file import.
* Screenshot OCR.
* Editing actual application screens.
* Automatic product code modifications.
* Live GitHub or GitLab integration.
* Real-time collaboration.
* Cloud-hosted inference.
* Translation and multilingual localization.
* Automated WCAG certification.
* Comprehensive screen-reader testing.
* Browser accessibility scanning.
* Mobile application deployment.
* Enterprise authentication.
* Database-backed user accounts.
* Automatic publication of revised interface strings.

# 6. Supported Component Types

Version 1 shall recognize:

| Component | Examples |
|---|---|
| Button | Save, Submit report, Cancel |
| Field label | Email address, Project name |
| Tooltip or helper text | Explain a configuration option |
| Error or warning message | Failed operation, risky action |
| Onboarding or empty state | Getting-started instructions |

Each component shall have a type, user context, source string, and configurable character limit.

Additional types may be introduced later without restructuring the core data model.

# 7. Primary User Workflow

1. User launches Microcopy Lab locally.
2. User creates a project or loads an example project.
3. User enters or imports interface strings.
4. Application validates the records and metadata.
5. User chooses a style guide.
6. User runs deterministic analysis.
7. User optionally runs local AI analysis.
8. Application displays findings and proposed revisions.
9. User examines the original and revised strings in a component preview.
10. User approves, rejects, or requests additional review.
11. User exports the selected content and audit report.

The source string remains unchanged unless the user explicitly edits the input record.

# 8. Functional Requirements

## FR-001: String Import and Manual Entry

The application shall support individual manual entry and batch import through CSV or JSON.

Required fields:

* String identifier.
* Component type.
* Original text.
* User or interface context.

Optional fields:

* Screen identifier.
* Product area.
* User goal.
* Maximum character length.
* Product behavior description.
* Design notes.
* Protected tokens.
* Source reference.

Requirements:

* Default maximum upload size of 5 MB.
* UTF-8 text processing.
* Configurable record count limit.
* Duplicate identifier detection.
* Validation of supported component types.
* Safe handling of malformed input.
* No execution of imported scripts or instructions.

CSV and JSON schemas shall be published in the repository.

## FR-002: Normalized UI String Model

Every imported string shall be represented through a validated internal data model.

The application shall preserve original string identifiers and metadata.

The normalized model shall distinguish between original content, editorial findings, AI suggestions, and accepted revisions.

## FR-003: Deterministic Editorial Checks

The application shall support:

* Discouraged terminology.
* Preferred terminology.
* Prohibited phrases.
* Character-limit violations.
* Empty or whitespace-only labels.
* Leading and trailing whitespace.
* Repeated punctuation.
* Duplicate strings with inconsistent terminology.
* Component-specific editorial rules.

Rules shall be configurable and independently testable.

A rule match shall not automatically establish that the string is defective. Context-dependent recommendations require editorial confirmation.

## FR-004: Contextual AI Review

Ollama shall analyze individual strings or small bounded groups of related strings.

The model shall consider:

* Component type.
* User intent.
* Original wording.
* Interface context.
* Available product behavior evidence.
* Editorial style configuration.
* Character constraints.

AI analysis shall identify potential concerns involving:

* Ambiguous wording.
* Unclear calls to action.
* Excessive technical jargon.
* Missing error recovery guidance.
* Inconsistent tone.
* Unexplained consequences.
* Confusing instructional sequences.
* Accessibility-related wording problems.

The model shall return structured findings rather than unrestricted narrative output.

## FR-005: Suggested Revisions

For each supported finding, the application may generate one or more revised strings.

Every suggestion shall include:

* Suggested text.
* Explanation.
* Finding category.
* Severity.
* Source string identifier.
* Relevant editorial rule.
* Human review status.
* An indication of whether product behavior confirmation is required.

Suggestions shall not invent product functionality, recovery procedures, availability, permissions, or technical capabilities.

When the source context is insufficient, the application shall generate an editorial clarification question instead of inventing the missing detail.

## FR-006: UX Writing Style Guide

The application shall load a validated YAML configuration containing:

* Style guide name and version.
* Brand voice.
* Target audience.
* Tone preferences.
* Terminology dictionary.
* Discouraged phrases.
* Component-specific character limits.
* Error message writing rules.
* Button label conventions.
* Placeholder preservation rules.
* Enabled audit categories.

The style guide shall be versioned so exported reports can identify the rules applied during analysis.

Custom configuration shall be treated as data, not executable code.

## FR-007: Interactive Interface Preview

The application shall display original and proposed copy inside simulated UI components.

Required preview templates:

1. Button and action area.
2. Form field and label.
3. Tooltip or helper text.
4. Error or warning alert.
5. Onboarding or empty-state panel.

Requirements:

* Display original and revised content.
* Permit toggling between versions.
* Show character usage.
* Flag length violations.
* Preserve punctuation and dynamic placeholders.
* Indicate when revised copy may not fit the selected layout.
* Escape imported or generated text before rendering.

Previews represent approximate design contexts. They do not prove text fit in actual production applications or across fonts, devices, and languages.

## FR-008: Accessibility-Related Writing Checks

The application shall flag potential writing concerns related to:

* Unclear labels.
* Missing instructions for user input.
* Errors lacking understandable explanations.
* Unclear recovery guidance.
* Ambiguous abbreviations.
* Inconsistent identification of repeated actions.
* Reliance on color descriptions without additional context.

Applicable reference topics may include WCAG 2.2 Success Criteria 3.3.1, 3.3.2, 3.3.3, and 3.2.4.

These are advisory checks only.

The application shall not claim to establish WCAG compliance, keyboard accessibility, accessible names, assistive technology compatibility, or screen-reader behavior.

## FR-009: Terminology Consistency

The application shall identify potentially inconsistent terminology across imported interface strings.

Example:

* Sign in versus Log in.
* Delete versus Remove.
* Workspace versus Project.
* User ID versus Username.

Configured terminology preferences shall take precedence over generic AI wording preferences.

Proper nouns, API names, protected product labels, and placeholder tokens shall not be silently changed.

## FR-010: Review and Approval

Every proposed revision shall support:

* Pending.
* Approved.
* Rejected.
* Needs Clarification.

The reviewer shall be able to record optional notes.

Approval applies to a specific revision version. Subsequent material edits shall reset approval.

No revision shall automatically overwrite the original source record.

## FR-011: Export

Supported formats:

* JSON audit and revision report.
* CSV string catalog with review statuses.
* Markdown editorial report.

Exports shall include:

* Project identifier.
* Application version.
* Active style guide version.
* Original string ID.
* Original text.
* Proposed revision.
* Finding category.
* Explanation.
* Review status.
* Applicable model identifier.
* Processing limitations.

Exports shall distinguish approved revisions from unreviewed suggestions.

## FR-012: Audit Summary

The application shall display:

* Total imported strings.
* Strings analyzed.
* Findings by category.
* Findings by severity.
* Pending review count.
* Approved revision count.
* Character-limit violations.
* Failed or partial analysis count.

The application shall not create a single overall UX quality score unless a validated scoring method is developed and documented.

# 9. Data Models

## 9.1 UI String

```json
{
  "schema_version": "1.0",
  "string_id": "UI-001",
  "screen_id": "REPORTS",
  "component_type": "button",
  "original_text": "Proceed",
  "context": "Submit a maintenance report for review",
  "max_chars": 24,
  "protected_tokens": [],
  "source_reference": "SCREEN-REPORTS-01"
}
```

## 9.2 Audit Finding

```json
{
  "finding_id": "F-001",
  "string_id": "UI-001",
  "category": "clarity",
  "severity": "medium",
  "detection_method": "ai_assisted",
  "explanation": "The button label does not identify the action.",
  "rule_id": "BUTTON-CLARITY-001",
  "review_status": "pending"
}
```

## 9.3 Proposed Revision

```json
{
  "revision_id": "REV-001",
  "string_id": "UI-001",
  "suggested_text": "Submit report",
  "rationale": "Names the action performed by the button.",
  "requires_behavior_confirmation": true,
  "protected_tokens_valid": true,
  "review_status": "pending"
}
```

## 9.4 Audit Session

An audit session shall record:

* Session identifier.
* Project identifier.
* Style guide version.
* Analysis methods used.
* Model identifier and configuration, if applicable.
* Imported string count.
* Findings and revisions.
* Validation warnings.
* Processing status.

All records may remain in memory for v1.

# 10. Technical Architecture

## 10.1 Architectural Requirements

Streamlit shall be the presentation layer only.

The application shall implement an independent Python package for:

* Input validation.
* Normalization.
* Terminology checks.
* Length validation.
* Contextual AI analysis.
* Suggested revision validation.
* Review state management.
* Report generation.

No core module may import Streamlit or access Streamlit session state.

All core functions must be callable independently through Python scripts and automated tests.

## 10.2 AI Adapter

Ollama integration shall be implemented as a separate adapter.

The adapter shall:

* Check local model availability.
* Use structured JSON output.
* Validate responses with Pydantic.
* Apply configurable timeouts.
* Limit input and output sizes.
* Avoid unrestricted tool execution.
* Return safe, typed errors.
* Permit deterministic-only operation when unavailable.

Model selection shall remain configurable.

## 10.3 Preview Architecture

The preview engine shall use structured component templates.

Imported content shall remain plain text and shall not be interpreted as executable HTML, JavaScript, or arbitrary template code.

The preview layout shall remain independent of the audit engine so it can be redesigned without modifying editorial logic.

# 11. Security and Privacy Requirements

## 11.1 Local Processing

All analysis shall occur on the local computer.

The application shall not transmit imported interface strings to external AI services.

No telemetry or cloud database is required.

Internet access may be necessary for dependency installation and model downloads but not for normal operation after setup.

## 11.2 File and Input Security

* Validate all imported fields.
* Enforce file and record limits.
* Reject malformed JSON and CSV.
* Treat imported content as untrusted data.
* Do not execute code embedded in strings.
* Do not follow links automatically.
* Do not allow arbitrary local file access through imported records.
* Reject or safely escape markup used in previews.
* Avoid storing full imported data in diagnostic logs.

## 11.3 Prompt Injection Protection

An imported string may contain malicious instructions directed at the model.

The application shall:

* Separate system instructions from string content.
* Treat imported strings as data.
* Prevent model tool access.
* Validate model output.
* Reject malformed suggestions.
* Protect reserved placeholders.
* Test malicious examples.
* Never allow source content to alter application configuration.

These controls mitigate prompt injection but cannot guarantee perfect resistance.

## 11.4 Placeholder and Token Integrity

Interface strings may contain dynamic tokens.

Examples:

* `{username}`
* `{count}`
* `%s`
* `${projectName}`

The application shall identify configured placeholder syntaxes, preserve required placeholders, and reject proposed revisions that remove, rename, or duplicate protected tokens improperly.

Unsupported placeholder formats must be documented.

## 11.5 Error Handling

User-facing error messages shall be understandable and shall not reveal internal paths, secrets, or stack traces.

Developer diagnostics shall identify the failing component without unnecessarily recording source content.

# 12. Testing Strategy

## 12.1 Deterministic Testing

Tests shall verify:

* Valid CSV and JSON import.
* Missing required fields.
* Duplicate identifiers.
* Unsupported component types.
* Character counting.
* Terminology matching.
* Placeholder preservation.
* Style guide validation.
* Review state transitions.
* Report export.

## 12.2 AI Integration Testing

Tests shall verify:

* Valid structured responses.
* Rejection of malformed JSON.
* Rejection of unsupported identifiers.
* Missing placeholder detection.
* Model unavailability handling.
* Incomplete analysis reporting.
* Clarification behavior where product context is insufficient.

Automated tests shall use mocked AI responses for reproducibility.

## 12.3 UX Evaluation

The sample dataset shall include human-authored expected improvements.

Evaluation shall examine:

* Relevance of suggestions.
* Preservation of product meaning.
* Terminology consistency.
* Character-limit compliance.
* Unsupported claim frequency.
* Editorial acceptance rates.

Performance claims shall be based on actual test results.

# 13. Acceptance Criteria

**AC-001:** Users can import valid CSV and JSON string catalogs.

**AC-002:** Users can manually add and edit UI string records.

**AC-003:** Deterministic rules identify configured terminology and length violations.

**AC-004:** Supported dynamic placeholders are preserved or invalid revisions are rejected.

**AC-005:** Valid source context produces structured AI findings.

**AC-006:** Unsupported product behavior is flagged for clarification rather than invented.

**AC-007:** Users can preview original and revised text in all five supported component templates.

**AC-008:** Imported HTML-like content is displayed as text and cannot execute scripts.

**AC-009:** Users can approve, reject, or request clarification for proposed revisions.

**AC-010:** Materially modifying approved content resets approval.

**AC-011:** Markdown, CSV, and JSON exports contain accurate source identifiers, revision records, and statuses.

**AC-012:** The application remains usable for deterministic analysis when Ollama is unavailable.

**AC-013:** Imported content cannot cause external network requests or arbitrary command execution.

**AC-014:** The application operates offline once dependencies and the local model are installed.

**AC-015:** Automated tests pass, and failures are documented accurately.

**AC-016:** The core Python engine has no Streamlit dependencies.

# 14. Sample Portfolio Dataset

The application shall include a fictional fleet maintenance SaaS interface.

**Sample Product:** FleetOps Demo

Example screens:

* Login and account management.
* Maintenance report submission.
* Equipment status dashboard.
* Notification preferences.
* Work-order administration.
* First-time user onboarding.

The dataset shall contain approximately 30 to 50 UI strings covering:

* Ambiguous buttons.
* Inconsistent terminology.
* Unclear error messages.
* Unhelpful tooltips.
* Excessive jargon.
* Character-limit violations.
* Protected dynamic tokens.
* Clear strings that should not be changed.
* Malicious prompt injection examples.

All product behavior shall be fictional and clearly identified as such.

Expected audit results shall be documented separately.

# 15. Development Milestones

## Milestone 1: Foundation

Create:

* Repository structure.
* Python package.
* Typed data models.
* CSV and JSON importers.
* Manual string entry.
* Style guide configuration.
* Initial Streamlit interface.
* Sample dataset.
* Initial tests.

**Exit criterion:** Users can import, inspect, and manually enter validated interface strings without AI.

## Milestone 2: Deterministic Analysis

Implement terminology checks, character limits, placeholder protection, component rules, and structured findings.

**Exit criterion:** Rule-based audits generate reproducible findings.

## Milestone 3: Local AI Integration

Integrate Ollama for contextual UX analysis, suggestions, and clarification questions.

**Exit criterion:** AI produces validated, source-linked recommendations using fictional test inputs.

## Milestone 4: Interactive Preview

Implement five predefined interface components and original/revised comparison.

**Exit criterion:** Users can meaningfully assess suggested copy in simulated interface contexts.

## Milestone 5: Editorial Review and Export

Implement approval states, review notes, audit summaries, and Markdown/CSV/JSON exports.

**Exit criterion:** Users can complete and export an editorial review session.

## Milestone 6: Testing and Portfolio Release

Complete integration testing, security validation, offline tests, project documentation, and a portfolio case study.

**Exit criterion:** All P0 requirements and acceptance tests pass.

# 16. Nonfunctional Requirements

## Reliability

Malformed files and failed AI requests shall not crash the application or destroy imported session records.

## Maintainability

Code shall use modular components, type hints, documented interfaces, and automated tests.

## Performance

Performance shall be evaluated using the sample catalog on actual development hardware. No unmeasured performance guarantees shall be advertised.

## Portability

Core logic shall be usable from a command-line application or future native desktop interface without rewriting the analysis engine.

## Privacy

No external document or string transmission shall occur during normal local processing.

# 17. Risks and Mitigations

| Risk | Mitigation |
|---|---|
| AI invents product behavior | Require context and clarification questions |
| Suggested copy changes meaning | Human review and source comparison |
| Placeholder corruption | Deterministic token validation |
| Incorrect terminology changes | Configurable product dictionary |
| Accessibility overclaims | Advisory findings and explicit limitations |
| Misleading previews | Label simulated components as approximations |
| Prompt injection | Untrusted input isolation and constrained model capabilities |
| Resource exhaustion | Input, record, timeout, and output limits |
| Inconsistent results | Versioned rules and model configuration |
| Scope expansion | Six bounded development milestones |

# 18. Future Roadmap

## Version 1.1

Potential enhancements:

* Additional UI preview components.
* Multiple editorial style profiles.
* Richer terminology dictionaries.
* Dark and light preview themes.
* Better detection of space-constrained copy.
* Optional comparison of revision versions.

## Version 2.0

Potential enhancements:

* Figma integration.
* Git-based string catalog integration.
* Localization support.
* Screenshot-based context extraction.
* Design-system component imports.
* Team editorial collaboration.
* Persistent project history.
* Native desktop packaging.

Future capabilities shall be evaluated separately and are not commitments for v1.

# 19. Definition of Done

Microcopy Lab v1 is complete when:

1. All P0 features are implemented.
2. CSV, JSON, and manual string entry work correctly.
3. Deterministic auditing is functional.
4. Ollama generates structured contextual suggestions.
5. Suggested revisions protect dynamic placeholders.
6. Five simulated component previews function correctly.
7. Human review decisions are implemented.
8. Reports export in all three supported formats.
9. Security and offline behavior are tested.
10. The independent Python engine has no Streamlit dependencies.
11. Automated tests pass.
12. Installation, architecture, methodology, limitations, and usage documentation are complete.
13. A reproducible portfolio demonstration is available.

# 20. Product Positioning

**Short Description**

Microcopy Lab is a local-first AI-assisted UX writing application that evaluates interface text, recommends clearer alternatives, and previews revisions in simulated software components.

**Portfolio Description**

Designed and developed a Python-based UX content analysis prototype using Streamlit, local LLM inference, configurable editorial standards, and structured content validation. The application demonstrates UX writing, terminology governance, accessibility awareness, and human-centered AI workflows.

**Core Principle**

Good interface writing communicates verified product behavior clearly. AI may recommend language, but humans remain responsible for correctness, usability, and approval.

4. Architecture and repository layout
The architecture deliberately keeps the analysis engine independent of Streamlit, consistent with your other projects.
Streamlit UI
Import · Analyze · Preview · Review · Export

Independent Microcopy Lab Python Engine
Validation · Rules · Suggestions · Review State · Reporting

Deterministic Checks
Terminology, length limits, protected tokens

Ollama Adapter
Contextual language analysis and suggestions



Proposed repository

microcopy-lab/
├── app.py
├── pyproject.toml
├── README.md
├── AGENTS.md
├── .gitignore
├── .streamlit/
│   └── config.toml
├── config/
│   └── ux_style_guide.yaml
├── src/
│   └── microcopy_lab/
│       ├── __init__.py
│       ├── models.py
│       ├── importers.py
│       ├── rules.py
│       ├── terminology.py
│       ├── placeholders.py
│       ├── engine.py
│       ├── ai_adapter.py
│       ├── revisions.py
│       ├── preview_models.py
│       ├── review.py
│       └── exporters.py
├── samples/
│   ├── fleetops_strings.csv
│   ├── fleetops_strings.json
│   └── expected_findings.json
├── tests/
│   ├── test_models.py
│   ├── test_importers.py
│   ├── test_rules.py
│   ├── test_placeholders.py
│   ├── test_engine.py
│   ├── test_revisions.py
│   └── test_security.py
└── docs/
    ├── PRD.md
    ├── architecture.md
    ├── methodology.md
    ├── security.md
    └── user_guide.md



Codex should only create files required by the current milestone, rather than populating every future module with placeholder code.
5. Codex kickoff prompt
This is the prompt I recommend using for the initial implementation. It establishes all the important engineering rules while limiting the first coding pass to Milestone 1.
Milestone 1: Project Foundation
Ready for Codex


You are the lead software engineer responsible for developing Microcopy Lab v1.

PROJECT
Microcopy Lab is a local-first AI UX Writing and Interface Content Assistant.

The application evaluates labels, buttons, tooltips, error messages, warnings, and onboarding instructions. Later milestones will use Ollama to recommend clearer wording and preview revisions inside simulated UI components.

Build MILESTONE 1 ONLY.

Use docs/PRD.md as the primary specification if it exists.

TECHNOLOGY STACK
- Python 3.12
- Streamlit for the local UI
- Pydantic v2 for data models
- PyYAML for configuration
- Standard-library csv and json
- pytest for automated testing
- Ruff for linting and formatting
- mypy for type checking
- pip-audit for dependency scanning
- Git for version control
- Ollama in a later milestone

ARCHITECTURAL REQUIREMENTS

1. Maintain a strict separation between Streamlit and the Python processing engine.

2. All core functionality must reside in src/microcopy_lab/.

3. No module in src/microcopy_lab/ may import Streamlit or depend on Streamlit session state.

4. The Python engine must be independently callable and testable.

5. Use typed functions and Pydantic models.

6. Keep the architecture compatible with a future native desktop interface.

7. Do not implement cloud services, authentication, or persistent databases.

8. Implement no external telemetry or network calls.

MILESTONE 1 DELIVERABLES

1. Initialize the project with a src-based Python package.

2. Create pyproject.toml with appropriate dependency definitions and development tools.

3. Create README.md, AGENTS.md, .gitignore, and documentation directories.

4. Create the initial Pydantic domain models:

   UIString
   ComponentType
   Project
   ImportResult
   ValidationWarning
   AuditFinding
   ProposedRevision
   ReviewStatus

5. Provide explicit schema versions and stable identifiers.

6. Define component types:

   button
   field_label
   tooltip
   error_warning
   onboarding_empty_state

7. Implement CSV and JSON import.

8. Implement manual UI string entry through Streamlit.

9. Validate required fields, component types, identifiers, and character limits.

10. Preserve all source IDs and product context.

11. Create config/ux_style_guide.yaml with example brand voice, terminology, character limits, and editorial preferences.

12. Create a Streamlit application with:

    Project overview
    String import
    Manual string entry
    String catalog table
    Validation summary
    Component type filtering

13. Create a fictional FleetOps Demo dataset containing approximately 40 UI strings.

Include examples of:

    Ambiguous buttons
    Inconsistent terminology
    Unclear error messages
    Poorly written tooltips
    Excessive jargon
    Character-limit problems
    Dynamic placeholders
    Clear text requiring no changes
    Malicious embedded instructions

14. Implement automated tests covering:

    Model validation
    CSV and JSON parsing
    Duplicate identifiers
    Missing required fields
    Unsupported component types
    UTF-8 input
    Oversized inputs
    Malformed input
    Safe treatment of embedded markup
    Preservation of source metadata

SECURITY REQUIREMENTS

- Local operation only.
- Bind Streamlit to localhost.
- Default upload limit: 5 MB per file.
- Enforce a configurable record-count limit.
- Treat all imported content as untrusted.
- Never execute imported code.
- Never follow imported URLs.
- Never render imported text as executable HTML.
- Do not use unsafe_allow_html for untrusted content.
- Do not log source string contents by default.
- Do not expose sensitive stack traces to users.
- Provide safe diagnostic errors.

OUT OF SCOPE FOR MILESTONE 1

- Ollama integration
- AI-generated suggestions
- Contextual AI analysis
- Full audit engine
- Dynamic component previews
- Approval workflow
- Final report exports
- Figma integration
- Cloud APIs
- Automatic product modifications
- User authentication
- Persistent database

QUALITY REQUIREMENTS

- Use modular, maintainable code.
- Add docstrings to public interfaces.
- Provide type hints.
- Create realistic sample data.
- Avoid unnecessary dependencies.
- Document limitations.
- Prefer simple solutions over premature abstractions.

TESTING

Run the available automated tests.

Run Ruff, mypy, and pip-audit where the environment permits.

Fix all feasible failures.

Do not claim tests pass unless they actually execute successfully.

Do not silently ignore dependency vulnerabilities.

DOCUMENTATION

Create:

README.md
docs/architecture.md
docs/security.md
docs/user_guide.md

The README must include installation, launch instructions, supported inputs, testing commands, and known limitations.

COMPLETION REPORT

After implementing Milestone 1, provide:

1. Files created
2. Architectural summary
3. Installation commands
4. Streamlit launch command
5. Actual test results
6. Known limitations
7. Security considerations
8. Readiness assessment for Milestone 2

Do not start Milestone 2 without a separate instruction.
  



6. Initial configuration example
The ux_style_guide.yaml file gives the project a practical editorial foundation.

name: "Microcopy Lab Default UX Guide"
version: "1.0"

audience: "General SaaS users"

voice:
  clear: true
  concise: true
  professional: true
  helpful: true
  avoid_blame: true

terminology:
  "log in": "sign in"
  "utilize": "use"
  "abort": "cancel"
  "execute": "run"

component_limits:
  button: 24
  field_label: 40
  tooltip: 120
  error_warning: 160
  onboarding_empty_state: 240

writing_rules:
  prefer_specific_actions: true
  avoid_unexplained_error_codes: true
  explain_recovery_steps_when_known: true
  preserve_product_meaning: true
  preserve_dynamic_placeholders: true

review:
  require_human_approval: true
  flag_unverified_behavior: true
  allow_rejection: true



These are example editorial rules, not universal standards. The application should make them configurable rather than assuming every software product uses the same voice, terminology, or component length limits.
7. Setting up Codex
Use a separate repository named microcopy-lab.
On your Mac, run:
mkdir -p ~/Projects/microcopy-lab
cd ~/Projects/microcopy-lab
git init


Then open the folder in Codex, save the PRD above as docs/PRD.md, and paste the Milestone 1 prompt.
Once the foundation is implemented, the application will typically launch using:
streamlit run app.py


The local address will ordinarily be http://localhost:8501, or the next available port if another Streamlit application is running.
8. Development sequence
1. Milestone 1: Project foundation
   Build the data models, sample catalog, import functionality, and initial Streamlit interface.
   Start in Codex
2. Milestone 2: Deterministic UX auditing
   Add terminology enforcement, character limits, component rules, and protected placeholder validation.
3. Milestone 3: AI recommendations
   Integrate Ollama with structured output, context-aware revisions, and unsupported-claim safeguards.
4. Milestone 4: Interactive UI previews
   Build simulated forms, buttons, tooltips, alerts, and onboarding panels with original/revised comparison.
5. Milestone 5: Editorial approval and exports
   Add review statuses, editorial notes, Markdown reports, CSV catalogs, and JSON results.
6. Milestone 6: QA and portfolio release
   Perform regression, security, and offline tests, then create screenshots, documentation, and a portfolio demonstration.

My recommendation for the portfolio
Microcopy Lab has one feature that I would particularly emphasize: side-by-side interface previews with editorial reasoning.
That gives an employer something visual and immediately understandable. They can see a poorly written error message, view the proposed improvement, and understand why the wording was changed.
It also complements the other two projects:
Application	Professional skill demonstrated
DocAudit AI	Technical documentation quality and editorial governance
Sprint2Docs AI	SDLC communication and release documentation
Microcopy Lab	UX writing, interface usability, and content design
Together, the three applications demonstrate how AI can assist a technical writer before, during, and after software development.
Next action: Launch Codex with the Microcopy Lab repository, provide the PRD, and run the Milestone 1 prompt. The initial deliverable should be a functional interface and sample string catalog, with no AI integration until the data foundation is tested.
That approach gives you a third distinct, credible portfolio project without unnecessarily increasing development complexity.