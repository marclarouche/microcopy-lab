# Deterministic methodology — engine deterministic-1.0
Every finding is advisory. The engine detects configured text patterns, not verified usability defects. It never rewrites source text or invents product behavior. Context-sensitive findings request behavior confirmation.

## Rule catalog
| Rule ID | Category | Severity | Trigger |
| --- | --- | --- | --- |
| TEXT-BLANK | whitespace | medium | Empty or whitespace-only raw text; imports reject this earlier |
| TEXT-EDGE-WHITESPACE | whitespace | low | Leading/trailing whitespace |
| TEXT-LENGTH | length | medium | Code-point length exceeds explicit source max_chars or component default |
| TEXT-REPEATED-PUNCTUATION | punctuation | low | Two or more question/exclamation marks, including mixed runs |
| TERM-PREFERRED | terminology | low | Configured discouraged term outside protected spans |
| PHRASE-PROHIBITED | prohibited_phrase | medium | Configured prohibited phrase outside protected spans |
| COMPONENT-GENERIC-LABEL | component | medium | Full text matches a configured generic component label |
| ERROR-CODE-ONLY | component | medium | Error/warning contains only a recognized code with optional Error prefix |
| TOKEN-DECLARED-MISSING | placeholders | high | Declared literal token does not occur in original text |
| CATALOG-TERM-VARIANTS | consistency | medium | Related strings canonicalize to the same copy through configured terminology |

Repeated periods are not flagged because ellipses can be intentional. Code-only detection covers hexadecimal, numeric, and letter-plus-digit codes; meaningful prose containing a code is not automatically flagged. Generic component labels match case-insensitively after whitespace normalization. The guide can configure labels for any of the five component types.

## Configuration
`enabled_categories` controls each rule family independently. Disabling terminology findings does not disable the separately enabled consistency category. Existing Milestone 1 guides remain valid through defaults. `component_rules` and `prohibited_phrases` default empty, while all categories and three built-in token syntaxes default enabled.

Terminology maps discouraged wording to a preferred term. Matching is case-insensitive, uses Unicode word boundaries, permits flexible whitespace between words, and never stems words. Regex metacharacters in configuration are escaped. Case/whitespace-equivalent keys, identity mappings, chains, and cycles are rejected. Overlapping distinct terms can legitimately yield multiple findings. Prohibited phrases must be distinct ignoring case/whitespace.

`protected_terms` masks configured product/API names from terminology/prohibited-phrase matches. Placeholders and explicit literal tokens are also excluded from those checks and from punctuation findings. Protected spans never suppress overall character limits or whitespace checks. A source's `max_chars` takes precedence over the style guide.

`writing_rules.prefer_specific_actions` controls generic button checks. `writing_rules.avoid_unexplained_error_codes` controls code-only errors. Other inherited editorial/voice flags are advisory guidance in the AI prompt; they do not generate extra deterministic checks. No rule infers a recovery step or verifies product behavior.

## Catalog consistency
Within the same screen identifier and component type, compare text after replacing configured discouraged terms with preferred terms, folding ordinary copy case, and normalizing whitespace. Different surface forms that share this canonical text receive related source IDs. A missing screen identifier forms an unspecified-screen group. Exact duplicates and case/whitespace-only differences do not receive consistency findings. Cross-screen inference, stemming, and fuzzy semantic similarity are excluded. Protected token spelling/case stays literal so different tokens do not establish equivalence. Even a match requires human confirmation that the concepts are actually equivalent.

## Placeholder protection
`token_spans` discovers built-in `{name}`, `${name}`, `%s`, `%d`, and `%f` tokens plus explicit literal `protected_tokens`. Names start with an ASCII letter/underscore and continue with letters/digits/underscores/dots. Escaped `%%` does not introduce printf placeholders. Double-brace templates, ICU expressions, positional/width printf, Unicode names, and other formats are unsupported unless declared literally. Configure built-ins using `placeholder_syntaxes`; explicit tokens remain protected regardless of built-in selection.

`validate_placeholder_integrity(source, candidate, syntaxes=guide.placeholder_syntaxes)` compares exact token multisets. Removal, renaming, case changes, duplicated occurrences, and newly introduced supported tokens invalidate the candidate. Token order may change and is not semantic validation. Missing declared source tokens also invalidate the candidate, even if the candidate adds them. An identical explicit/automatic token span is counted once; explicit prefixes cannot hide recognized built-in tokens. The AI candidate gate enforces `valid`; no candidate is applied automatically. This API is not an approval workflow.

Custom tokens are literal, nonblank, at most 200 code points each, and limited to 1,000 declarations per source. Candidate strings are bounded to 100,000 code points. Rule switches do not silently authorize dropping declared tokens: the integrity helper always validates the configured token formats.

## Sample acceptance
`samples/expected_findings.json` contains human-authored rule expectations for all deterministic findings in the bundled FleetOps guide. Fifteen of 40 strings have one finding each, with three length violations. Unlisted strings have no configured matches, which does not prove their wording is good. Hostile strings remain inert; deterministic editorial rules are not a prompt-injection detector. See `samples/expected_findings.md` for contextual concerns reserved for later milestones.

## Contextual AI methodology
Milestone 3 supplements deterministic checks with optional local model findings; it does not replace or silently merge the two result sets. Strict schemas constrain categories and source links, while application-owned evidence, token, fit, protected-name, terminology, vocabulary, polarity and number checks gate candidates. Missing context leads to clarification. These lexical gates cannot certify meaning preservation; all candidates remain pending and require human behavior confirmation. Detailed request policy and limits are in local_ai.md. Mocked outputs test mechanics, while live inference is a separate smoke check with no automatic accuracy claims.
