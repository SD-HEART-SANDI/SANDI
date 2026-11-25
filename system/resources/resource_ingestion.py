"""
File Name: resource_ingestion.py
Purpose: Turn a CSV or JSON file of services into checked SANDI Resource records (DATA-002)
Goals:
- Read service records from a CSV or JSON file
- Check every record against the Resource schema (system/models/resources.py)
- Flag broken records and duplicate IDs with a plain reason
- Write the good records to JSON and a validation report to Markdown
Run:
    python -m system.resources.resource_ingestion data/mock/mock_resources_raw.csv
Architecture Decision:
Keeps going when a record is broken: one bad row is reported, not a crash for the whole file
"""
import argparse
import csv
import json
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from pydantic import ValidationError

from system.config import settings
from system.models.resources import Resource


@dataclass
class InvalidRecord:
    row: int  #position in the file, starting at 1
    record_id: str  #id from the file, or "(missing)"
    errors: list[str]  #plain reasons why the record was rejected


@dataclass
class IngestionResult:
    source_file: str
    valid: list[Resource] = field(default_factory=list)
    invalid: list[InvalidRecord] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.valid) + len(self.invalid)


"""
Reading files
"""
def parse_hours(text: str) -> list[dict]:
    """
    Turn CSV hours text into a list of open periods.
    Format: "mon 09:00-17:00; wed 11:00-13:00". Empty text means hours are unknown.
    """
    hours: list[dict] = []
    for part in text.split(";"):
        part = part.strip()
        if not part:
            continue
        try:
            day, times = part.split()
            opens, closes = times.split("-")
        except ValueError:
            raise ValueError(f"hours: '{part}' should look like 'mon 09:00-17:00'")
        hours.append({"day": day.lower(), "opens": opens, "closes": closes})
    return hours


def load_csv(file_path: Path) -> list[dict]:
    with open(file_path, newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))
    #Empty CSV cells become None so optional fields stay optional
    return [{key: (value.strip() or None) if value is not None else None
             for key, value in row.items()} for row in rows]


def load_json(file_path: Path) -> list[dict]:
    with open(file_path, encoding="utf-8") as file:
        data = json.load(file)
    #Accept a plain list or {"resources": [...]}
    if isinstance(data, dict):
        data = data.get("resources", [])
    if not isinstance(data, list):
        raise ValueError("INGESTION ERROR: JSON must be a list of records or {'resources': [...]}")
    return data


def load_records(file_path: Path) -> list[dict]:
    if not file_path.exists():
        raise FileNotFoundError(f"INGESTION ERROR: File {file_path} does not exist")
    suffix = file_path.suffix.lower()
    if suffix == ".csv":
        return load_csv(file_path)
    if suffix == ".json":
        return load_json(file_path)
    raise ValueError(f"INGESTION ERROR: {suffix} files are not supported (use .csv or .json)")


"""
Checking records
"""
def plain_errors(error: ValidationError) -> list[str]:
    #Turn pydantic errors into short readable lines, e.g. "latitude: must be >= 32.5"
    lines = []
    for item in error.errors():
        location = ".".join(str(part) for part in item["loc"]) or "record"
        lines.append(f"{location}: {item['msg']}")
    return lines


def validate_records(records: list[dict], source_file: str = "") -> IngestionResult:
    result = IngestionResult(source_file=source_file)
    seen_ids: set[str] = set()

    for row, record in enumerate(records, start=1):
        record_id = (record.get("id") if isinstance(record, dict) else None) or "(missing)"

        if not isinstance(record, dict):
            result.invalid.append(InvalidRecord(row, record_id, ["record: must be an object"]))
            continue

        record = dict(record)
        #CSV hours arrive as text and must be split into open periods first
        if isinstance(record.get("hours"), str) or record.get("hours") is None:
            try:
                record["hours"] = parse_hours(record.get("hours") or "")
            except ValueError as error:
                result.invalid.append(InvalidRecord(row, record_id, [str(error)]))
                continue

        try:
            resource = Resource(**record)
        except ValidationError as error:
            result.invalid.append(InvalidRecord(row, record_id, plain_errors(error)))
            continue

        #VALIDATION: the same ID twice in one file
        if resource.id in seen_ids:
            result.invalid.append(InvalidRecord(row, record_id, [f"id: '{resource.id}' is used more than once"]))
            continue

        seen_ids.add(resource.id)
        result.valid.append(resource)

    return result


"""
Writing output
"""
def write_valid_records(result: IngestionResult, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    data = {"source_file": result.source_file,
            "resources": [resource.model_dump(mode="json") for resource in result.valid]}
    output_path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def write_report(result: IngestionResult, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Resource Validation Report",
        "",
        f"- Source file: `{result.source_file}`",
        f"- Date: {date.today().isoformat()}",
        f"- Records read: {result.total}",
        f"- Valid: {len(result.valid)}",
        f"- Invalid: {len(result.invalid)}",
        "",
    ]
    if result.invalid:
        lines += ["## Invalid records", "", "| Row | ID | Problem |", "|---|---|---|"]
        for bad in result.invalid:
            lines.append(f"| {bad.row} | {bad.record_id} | {'; '.join(bad.errors)} |")
    else:
        lines.append("All records are valid.")
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def ingest_resources(file_path: Path, output_dir: Path) -> IngestionResult:
    """Read, check, and write output for one file. Returns the result."""
    records = load_records(file_path)
    result = validate_records(records, source_file=str(file_path))
    write_valid_records(result, output_dir / "resources.json")
    write_report(result, output_dir / "resource_validation_report.md")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Check a CSV or JSON file of SANDI resources.")
    parser.add_argument("file", type=Path, help="CSV or JSON file of resources")
    parser.add_argument("--output-dir", type=Path, default=Path(settings.PROCESSED_DATA_DIR),
                        help="where to write resources.json and the report (default: data/processed)")
    args = parser.parse_args()

    result = ingest_resources(args.file, args.output_dir)
    print(f"Read {result.total} records: {len(result.valid)} valid, {len(result.invalid)} invalid.")
    print(f"Report: {args.output_dir / 'resource_validation_report.md'}")


if __name__ == "__main__":
    main()
