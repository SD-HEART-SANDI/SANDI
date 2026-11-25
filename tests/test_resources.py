"""
File Name: test_resources.py
Purpose: Unit tests for the SANDI resource schema (DATA-001)
Goals:
- All sample records in data/mock/mock_resources.json are valid
- Broken records are rejected
"""
import json
from datetime import date, timedelta
from pathlib import Path

import pytest
from pydantic import ValidationError

from system.models.resources import Resource

SAMPLE_FILE = Path(__file__).parent.parent / "data" / "mock" / "mock_resources.json"


def load_sample_records() -> list[dict]:
    with open(SAMPLE_FILE) as file:
        return json.load(file)["resources"]


def valid_record() -> dict:
    #Copy of one good record to break on purpose
    return dict(load_sample_records()[0])


def test_sample_records_are_valid():
    records = load_sample_records()
    resources = [Resource(**record) for record in records]
    assert 10 <= len(resources) <= 20


def test_sample_ids_are_unique():
    ids = [record["id"] for record in load_sample_records()]
    assert len(ids) == len(set(ids))


def test_overnight_hours_are_allowed():
    record = valid_record()
    record["hours"] = [{"day": "mon", "opens": "18:00", "closes": "07:00"}]
    assert Resource(**record).hours[0].closes.hour == 7


@pytest.mark.parametrize("field, bad_value", [
    ("id", "Food 1"),               #wrong ID format
    ("name", ""),                   #empty name
    ("category", "restaurant"),     #not an allowed category
    ("latitude", 40.7),             #New York, outside San Diego
    ("longitude", -74.0),           #New York, outside San Diego
    ("eligibility", ""),            #empty eligibility
    ("source", ""),                 #empty source
    ("hours", [{"day": "mon", "opens": "09:00", "closes": "09:00"}]),  #same open and close
    ("hours", [{"day": "monday", "opens": "09:00", "closes": "17:00"}]),  #bad day name
])
def test_bad_values_are_rejected(field, bad_value):
    record = valid_record()
    record[field] = bad_value
    with pytest.raises(ValidationError):
        Resource(**record)


@pytest.mark.parametrize("field", ["id", "name", "category", "latitude", "longitude",
                                   "eligibility", "source", "last_verified"])
def test_missing_required_field_is_rejected(field):
    record = valid_record()
    del record[field]
    with pytest.raises(ValidationError):
        Resource(**record)


def test_future_verification_date_is_rejected():
    record = valid_record()
    record["last_verified"] = (date.today() + timedelta(days=1)).isoformat()
    with pytest.raises(ValidationError):
        Resource(**record)


def test_unknown_field_is_rejected():
    record = valid_record()
    record["phone_number"] = "555-0100"
    with pytest.raises(ValidationError):
        Resource(**record)
