"""
File Name: resources.py
Purpose: Python class model for one SANDI resource: a real place that helps people
         (food, shelter, health care, hygiene, benefits)
Goals:
- Hold everything SANDI needs to know about one place: what, where, when, who, and source
- Reject broken records (missing ID, location outside San Diego, bad hours, future dates)
- Field definitions are explained in docs/resource_schema.md
Architecture Decision:
pydantic BaseModel (frozen) instead of @dataclass: same immutable typed object as the other
models, but it also checks every field when a record is loaded from CSV/JSON (needed by DATA-002)
"""
from datetime import date, time
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

#Allowed service types
ServiceCategory = Literal["food", "shelter", "health", "hygiene", "benefits", "other"]

#Allowed days of the week
Weekday = Literal["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

#San Diego County bounding box: any location outside this box is a data error
SD_MIN_LATITUDE, SD_MAX_LATITUDE = 32.5, 33.5
SD_MIN_LONGITUDE, SD_MAX_LONGITUDE = -117.6, -116.0


class OpeningHours(BaseModel):
    """One open period on one day. If closes is earlier than opens, it runs overnight."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    day: Weekday
    opens: time
    closes: time

    @field_validator("closes")
    @classmethod
    def closes_differs_from_opens(cls, closes: time, info) -> time:
        #VALIDATION: open and close at the same time means a typo
        if info.data.get("opens") == closes:
            raise ValueError("opens and closes cannot be the same time")
        return closes


class Resource(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str = Field(pattern=r"^[a-z]+-\d{3,}$")  #format: category-number, e.g. food-001
    name: str = Field(min_length=1)  #name of the place or program
    category: ServiceCategory  #type of service
    latitude: float = Field(ge=SD_MIN_LATITUDE, le=SD_MAX_LATITUDE)  #WGS84
    longitude: float = Field(ge=SD_MIN_LONGITUDE, le=SD_MAX_LONGITUDE)  #WGS84
    address: str | None = None  #street address, if known
    hours: tuple[OpeningHours, ...] = ()  #empty means hours are unknown
    eligibility: str = Field(min_length=1)  #who can use it, in plain words
    source: str = Field(min_length=1)  #where the information came from (link or organization)
    last_verified: date  #date someone last checked this information

    @field_validator("last_verified")
    @classmethod
    def not_in_future(cls, value: date) -> date:
        #VALIDATION: a check cannot happen in the future
        if value > date.today():
            raise ValueError("last_verified cannot be in the future")
        return value
