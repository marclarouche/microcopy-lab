# Input schema 1.0
JSON input is an array of UIString objects. CSV input uses object keys as headers, one object per row. See ../schemas/ui_string.schema.json for the generated JSON Schema and ../samples for complete examples.

Required: string_id (nonblank without whitespace/control characters), component_type (one of five enum values), original_text and context (nonblank strings up to 100,000 code points). Source whitespace is preserved. schema_version defaults to 1.0 and rejects other versions.

Optional max_chars is an integer from 1 through 100,000, or null/CSV blank. protected_tokens defaults to an empty list and accepts strings only; in CSV use a JSON array cell such as `["{count}"]`, with standard CSV quoting. Other known optional metadata fields accept text or null. Unknown JSON fields preserve their values; unknown CSV columns preserve text.

Duplicate CSV headers, duplicate JSON object keys, extra/missing CSV cells, invalid UTF-8, unsupported file structures, invalid quoting, invalid numeric CSV cells, or malformed protected-token JSON reject the whole file. Invalid domain records and duplicate IDs reject individual rows. Row numbers refer to data records (header excluded). CSV has no automatic delimiter detection; use comma-separated files. Import warnings are data validation only, not an editorial audit.

Milestone 2 adds bounded nonblank protected-token declarations: up to 1,000 strings, each at most 200 code points. Duplicate declarations do not multiply the required occurrence count. Declaration presence is checked by the audit; an absent declared token is retained at import and reported as a source-metadata finding. The UIString schema version remains 1.0. Additional schemas publish audit results, token validation, and style-guide configuration; these are API contracts, not new catalog import formats.
