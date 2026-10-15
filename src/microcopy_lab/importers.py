"""Bounded UTF-8 import with row diagnostics and lossless metadata."""

import csv
import io
import json
from collections.abc import Iterable
from typing import Any, Literal

from pydantic import ValidationError

from microcopy_lab.config import StyleGuide
from microcopy_lab.models import ImportResult, UIString, ValidationWarning

MAX_UPLOAD_BYTES = 5 * 1024 * 1024


def diagnostic(code: str, message: str, row: int | None = None) -> ValidationWarning:
    """Build a diagnostic without interpolating untrusted content."""
    return ValidationWarning(code=code, message=message, row=row)


def validate_records(
    records: Iterable[object], *, guide: StyleGuide, existing: Iterable[UIString] = ()
) -> ImportResult:
    """Validate a bounded batch; retain valid rows, rejecting duplicate IDs."""
    prior = list(existing)
    seen = {item.string_id for item in prior}
    result = ImportResult()
    for row, raw in enumerate(records, 1):
        if row + len(prior) > guide.max_records:
            return ImportResult(
                fatal=True,
                warnings=[
                    diagnostic("record_limit", "Record limit exceeded; batch was not imported.")
                ],
            )
        try:
            item = UIString.model_validate(raw)
        except (ValidationError, ValueError, TypeError):
            result.rejected_count += 1
            result.warnings.append(
                diagnostic(
                    "invalid_record", "Check required fields, types, identifiers and limits.", row
                )
            )
            continue
        if item.string_id in seen:
            result.rejected_count += 1
            result.warnings.append(
                diagnostic("duplicate_id", "Identifier already exists; row skipped.", row)
            )
            continue
        seen.add(item.string_id)
        result.strings.append(item)
        limit = (
            item.max_chars if item.max_chars is not None else guide.limit_for(item.component_type)
        )
        if len(item.original_text) > limit:
            result.warnings.append(
                ValidationWarning(
                    code="character_limit",
                    message=f"Text exceeds the {limit}-character limit.",
                    row=row,
                    string_id=item.string_id,
                    severity="warning",
                )
            )
    return result


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key")
        result[key] = value
    return result


def import_catalog(
    data: bytes,
    format: Literal["csv", "json"],
    *,
    guide: StyleGuide,
    existing: Iterable[UIString] = (),
) -> ImportResult:
    """Parse CSV or a JSON array. Malformed files are rejected atomically."""
    if len(data) > MAX_UPLOAD_BYTES:
        return ImportResult(fatal=True, warnings=[diagnostic("file_size", "File exceeds 5 MB.")])
    try:
        text = data.decode("utf-8-sig")
        records: list[object] = []
        if format == "json":
            parsed = json.loads(
                text,
                object_pairs_hook=_pairs,
                parse_constant=lambda value: (_ for _ in ()).throw(ValueError()),
            )
            if not isinstance(parsed, list):
                raise ValueError("Expected array")
            records = parsed
        elif format == "csv":
            reader = csv.DictReader(io.StringIO(text, newline=""), strict=True)
            fields = reader.fieldnames
            if (
                not fields
                or len(fields) != len(set(fields))
                or not {"string_id", "component_type", "original_text", "context"}.issubset(fields)
            ):
                raise ValueError("Invalid header")
            for row in reader:
                if None in row or any(value is None for value in row.values()):
                    raise ValueError("Invalid row width")
                record: dict[str, object] = dict(row)
                if "max_chars" in record:
                    record["max_chars"] = (
                        int(str(record["max_chars"])) if record["max_chars"] else None
                    )
                if "protected_tokens" in record:
                    record["protected_tokens"] = json.loads(str(record["protected_tokens"]) or "[]")
                records.append(record)
                if len(records) > guide.max_records:
                    break
        else:
            raise ValueError("Unsupported format")
        return validate_records(records, guide=guide, existing=existing)
    except (UnicodeError, ValueError, TypeError, csv.Error, RecursionError, OverflowError):
        return ImportResult(
            fatal=True,
            warnings=[
                diagnostic(
                    "malformed_input",
                    "Cannot read file. Check UTF-8 encoding and the documented format.",
                )
            ],
        )
