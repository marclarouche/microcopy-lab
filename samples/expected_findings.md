# Human-authored editorial examples
FLEET-001/002: clarify the action; confirm behavior first.
FLEET-004/005 and 014/015: investigate terminology consistency.
FLEET-007/012/020: character-limit warnings in Milestone 1.
FLEET-016/018: tooltips need useful context; 017/029 contain jargon.
FLEET-021/022: missing cause or recovery information; do not invent recovery.
FLEET-008/013/019/024/030/032/040: clear text may require no changes.
FLEET-025/026/027/031/039: preserve dynamic tokens in later revisions.
FLEET-036/037/038: hostile data must remain inert plain text.
These are editorial examples, not generated findings or universal judgments.

## Milestone 2 acceptance
`expected_findings.json` is the exact deterministic rule expectation for the bundled YAML guide: 15 findings on 15 strings. FLEET-003/004/006/017 match terminology; FLEET-007/012/020 exceed limits; FLEET-001/002/016/018/022/028 match generic component labels; FLEET-021 is a code-only error; FLEET-023 matches a configured prohibited phrase. Other contextual observations above remain for later analysis and are not claimed as deterministic detections.

The demo's Log in/Sign in labels occur on different screen IDs, so the conservative same-screen consistency rule does not group them. Dedicated tests cover related terminology variants. Dynamic-token examples are intact, so no placeholder metadata findings are expected. None of the hostile examples executes or changes configuration.
