"""Milestone 1 domain, import, security, and UI regression coverage."""

import ast
import csv
import io
import json
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from microcopy_lab.config import load_style_guide
from microcopy_lab.importers import MAX_UPLOAD_BYTES, import_catalog, validate_records
from microcopy_lab.models import Project, UIString

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def guide():
    return load_style_guide(ROOT / "config/ux_style_guide.yaml")


@pytest.fixture
def row():
    return {
        "string_id": "id-1",
        "component_type": "button",
        "original_text": "Save",
        "context": "Save report",
    }


def test_models(row):
    item = UIString(**row)
    assert item.schema_version == "1.0"
    assert UIString.model_validate_json(item.model_dump_json()) == item
    project = Project(name="Test", strings=[item])
    assert Project.model_validate_json(project.model_dump_json()).project_id == project.project_id
    with pytest.raises(ValidationError):
        Project(name="Test", strings=[item, item])


@pytest.mark.parametrize(
    "field,value",
    [
        ("string_id", "bad id"),
        ("string_id", ""),
        ("component_type", "link"),
        ("original_text", "  "),
        ("context", ""),
        ("max_chars", 0),
        ("max_chars", -1),
        ("max_chars", True),
        ("max_chars", "24"),
        ("schema_version", "2.0"),
        ("protected_tokens", [1]),
    ],
)
def test_invalid_model(row, field, value):
    with pytest.raises(ValidationError):
        UIString(**(row | {field: value}))


@pytest.mark.parametrize("field", ["string_id", "component_type", "original_text", "context"])
def test_missing(row, guide, field):
    del row[field]
    result = validate_records([row], guide=guide)
    assert result.rejected_count == 1 and not result.strings


def test_json_metadata_utf8_markup(row, guide):
    text = "<script>alert(1)</script> Café 🚚 {count} %s ${name}"
    row |= {
        "original_text": text,
        "custom": {"nested": ["https://example.invalid"]},
        "protected_tokens": ["{count}", "%s", "${name}"],
        "source_reference": "source-1",
    }
    result = import_catalog(json.dumps([row], ensure_ascii=False).encode(), "json", guide=guide)
    assert result.strings[0].original_text == text
    assert result.strings[0].model_dump()["custom"] == row["custom"]
    assert result.strings[0].source_reference == "source-1"
    assert result.strings[0].protected_tokens == row["protected_tokens"]


def test_csv_metadata(row, guide):
    row |= {
        "original_text": ' Save, "café"\nnow ',
        "max_chars": "24",
        "protected_tokens": '["{count}"]',
        "custom": "keep",
    }
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=list(row))
    writer.writeheader()
    writer.writerow(row)
    result = import_catalog(stream.getvalue().encode("utf-8-sig"), "csv", guide=guide)
    assert result.strings[0].original_text == row["original_text"]
    assert result.strings[0].max_chars == 24
    assert result.strings[0].model_dump()["custom"] == "keep"


def test_duplicates_and_existing(row, guide):
    result = validate_records([row, row], guide=guide)
    assert len(result.strings) == 1 and result.rejected_count == 1
    second = validate_records([row], guide=guide, existing=result.strings)
    assert not second.strings and second.warnings[0].code == "duplicate_id"


@pytest.mark.parametrize(
    "payload,kind",
    [
        (b"{", "json"),
        (b"{}", "json"),
        (b'[{"x":1,"x":2}]', "json"),
        (b"[NaN]", "json"),
        (b"\xff", "json"),
        (b"string_id,string_id\na,b", "csv"),
        (b"wrong\na", "csv"),
        (b"string_id,component_type,original_text,context\nx,button,save", "csv"),
        (b'string_id,component_type,original_text,context\nx,button,"unclosed', "csv"),
    ],
)
def test_malformed(payload, kind, guide):
    result = import_catalog(payload, kind, guide=guide)
    assert result.fatal and not result.strings
    assert "Traceback" not in result.warnings[0].message


def test_size_record_and_field_limits(row, guide):
    assert import_catalog(b" " * (MAX_UPLOAD_BYTES + 1), "json", guide=guide).fatal
    guide.max_records = 1
    assert validate_records([row, row | {"string_id": "other"}], guide=guide).fatal
    assert validate_records([row], guide=guide, existing=[UIString(**row)]).fatal
    assert (
        validate_records([row | {"original_text": "x" * 100001}], guide=guide).rejected_count == 1
    )


def test_partial_and_safe_diagnostic(row, guide):
    secret = "SECRET-SOURCE-CONTENT"
    result = validate_records([row, row | {"component_type": secret}], guide=guide)
    assert len(result.strings) == 1 and result.rejected_count == 1
    assert secret not in result.warnings[0].model_dump_json()


def test_character_limits(row, guide):
    result = validate_records([row | {"original_text": "🚚é", "max_chars": 1}], guide=guide)
    assert len(result.strings) == 1
    assert result.warnings[0].code == "character_limit"
    assert not validate_records([row | {"max_chars": 4}], guide=guide).warnings


def test_samples(guide):
    results = [
        import_catalog((ROOT / f"samples/fleetops_strings.{kind}").read_bytes(), kind, guide=guide)
        for kind in ("csv", "json")
    ]
    assert all(len(result.strings) == 40 for result in results)
    assert [r.model_dump() for r in results[0].strings] == [
        r.model_dump() for r in results[1].strings
    ]


def test_bad_yaml(tmp_path):
    path = tmp_path / "bad.yaml"
    path.write_text('!!python/object/apply:os.system ["echo unsafe"]')
    with pytest.raises(yaml.YAMLError):
        load_style_guide(path)


def test_engine_is_independent():
    for path in (ROOT / "src/microcopy_lab").glob("*.py"):
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                assert all(not alias.name.startswith("streamlit") for alias in node.names)
            if isinstance(node, ast.ImportFrom):
                assert not (node.module or "").startswith("streamlit")


def test_ui_smoke():
    from streamlit.testing.v1 import AppTest

    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()
    assert not app.exception
    app.button[1].click().run()
    assert not app.exception
    assert len(app.session_state.project.strings) == 40
    app.button[1].click().run()
    assert len(app.session_state.project.strings) == 40
    assert not app.exception


def test_ui_manual_and_filter():
    from streamlit.testing.v1 import AppTest

    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()
    app.text_input[1].set_value("MANUAL-001")
    app.text_area[1].set_value('<script>alert("inert")</script> {count}')
    app.text_area[2].set_value("Fictional count confirmation")
    app.button[2].click().run()
    assert not app.exception
    assert len(app.session_state.project.strings) == 1
    assert app.session_state.project.strings[0].original_text.startswith("<script>")
    app.multiselect[0].set_value(["tooltip"]).run()
    assert app.dataframe[0].value.empty
    app.multiselect[0].set_value(["button"]).run()
    assert len(app.dataframe[0].value) == 1
