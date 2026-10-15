"""Reproduce a fictional offline editorial session; never loads a user's session."""

import argparse
from pathlib import Path

from microcopy_lab.config import load_style_guide
from microcopy_lab.exporters import build_report, export_csv, export_json, export_markdown
from microcopy_lab.importers import import_catalog
from microcopy_lab.models import Project, ProposedRevision, ReviewStatus
from microcopy_lab.review import ReviewEntry, create_entry, update_entry

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    """Write reproducible fictional review artifacts with scripted example decisions."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "work/demo-output")
    args = parser.parse_args()
    guide = load_style_guide(ROOT / "config/ux_style_guide.yaml")
    imported = import_catalog(
        (ROOT / "samples/guided_test/01-guided-catalog.json").read_bytes(), "json", guide=guide
    )
    if imported.fatal or imported.rejected_count:
        raise SystemExit("The local fictional demo catalog could not be validated.")
    project = Project(
        name="FleetOps — scripted portfolio demonstration",
        product_context="Fictional offline demonstration. Decisions are scripted examples, not reviews of a real product.",
        strings=imported.strings,
    )
    examples = [
        (
            "TEST-001",
            "Submit report",
            "Names the fictional verified submission action.",
            ReviewStatus.APPROVED,
        ),
        (
            "TEST-001",
            "Continue",
            "Alternative rejected because it does not name the action.",
            ReviewStatus.REJECTED,
        ),
        (
            "TEST-003",
            "Use the maintenance filter",
            "Pending editorial review of helper wording.",
            ReviewStatus.PENDING,
        ),
        (
            "TEST-008",
            "Error 0x8004",
            "Placeholder draft; ask the product owner about cause and recovery.",
            ReviewStatus.NEEDS_CLARIFICATION,
        ),
    ]
    entries: list[ReviewEntry] = []
    for identifier, text, rationale, status in examples:
        revision = ProposedRevision(
            string_id=identifier,
            suggested_text=text,
            rationale=rationale,
            category="editorial",
            rule_id="SCRIPTED-DEMO",
        )
        entry = create_entry(project, guide, revision, origin="manual")
        entries.append(
            update_entry(
                entry,
                project,
                guide,
                text=text,
                rationale=rationale,
                notes="Scripted fictional demonstration only.",
                status=status,
                behavior_confirmed=status == ReviewStatus.APPROVED,
                others=entries,
            )
        )
    report = build_report(project, guide, entries)
    args.output.mkdir(parents=True, exist_ok=True)
    for name, data in {
        "review.json": export_json(report),
        "catalog.csv": export_csv(report),
        "review.md": export_markdown(report),
        "approved.csv": export_csv(report, approved_only=True),
    }.items():
        (args.output / name).write_text(data, encoding="utf-8", newline="")
    print(
        "Fictional offline demo: 9 strings, 7 deterministic findings, 4 review drafts, 1 approved replacement."
    )
    print("Wrote review.json, catalog.csv, review.md, and approved.csv.")


if __name__ == "__main__":
    main()
