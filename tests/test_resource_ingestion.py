"""
File Name: test_resource_ingestion.py
Purpose: Unit tests for resource ingestion (DATA-002)
Goals:
- CSV and JSON files load
- Good records pass, broken records are flagged with a reason
- Output JSON and validation report are written
"""
import json
from pathlib import Path

import pytest

from system.resources.resource_ingestion import (
    ingest_resources, load_records, parse_hours, validate_records,
)

MOCK_DIR = Path(__file__).parent.parent / "data" / "mock"
SAMPLE_CSV = MOCK_DIR / "mock_resources_raw.csv"
SAMPLE_JSON = MOCK_DIR / "mock_resources.json"


def test_parse_hours():
    assert parse_hours("mon 09:00-17:00; wed 11:00-13:00") == [
        {"day": "mon", "opens": "09:00", "closes": "17:00"},
        {"day": "wed", "opens": "11:00", "closes": "13:00"},
    ]
    assert parse_hours("") == []


def test_parse_hours_rejects_bad_text():
    with pytest.raises(ValueError):
        parse_hours("monday 6pm to 7am")


def test_json_sample_is_all_valid():
    result = validate_records(load_records(SAMPLE_JSON))
    assert len(result.valid) == 12
    assert result.invalid == []


def test_csv_sample_flags_bad_rows():
    result = validate_records(load_records(SAMPLE_CSV))
    assert len(result.valid) == 6
    flagged_rows = {bad.row for bad in result.invalid}
    assert flagged_rows == {7, 8, 9, 10, 11, 12}


def test_duplicate_id_is_flagged():
    result = validate_records(load_records(SAMPLE_CSV))
    duplicate = next(bad for bad in result.invalid if bad.row == 11)
    assert "more than once" in duplicate.errors[0]


def test_errors_name_the_field():
    result = validate_records(load_records(SAMPLE_CSV))
    wrong_place = next(bad for bad in result.invalid if bad.row == 8)
    assert any(error.startswith("latitude") for error in wrong_place.errors)


def test_unsupported_file_type(tmp_path: Path):
    bad_file = tmp_path / "resources.txt"
    bad_file.write_text("hello")
    with pytest.raises(ValueError):
        load_records(bad_file)


def test_missing_file():
    with pytest.raises(FileNotFoundError):
        load_records(Path("does_not_exist.csv"))


def test_output_files_are_written(tmp_path: Path):
    result = ingest_resources(SAMPLE_CSV, tmp_path)

    saved = json.loads((tmp_path / "resources.json").read_text())
    assert len(saved["resources"]) == len(result.valid)

    report = (tmp_path / "resource_validation_report.md").read_text()
    assert "Valid: 6" in report
    assert "Invalid: 6" in report


def test_same_input_gives_same_output(tmp_path: Path):
    #Reproducible: running twice gives the same records
    ingest_resources(SAMPLE_CSV, tmp_path / "run1")
    ingest_resources(SAMPLE_CSV, tmp_path / "run2")
    assert (tmp_path / "run1" / "resources.json").read_text() == \
           (tmp_path / "run2" / "resources.json").read_text()
