# SANDI Resource Schema (DATA-001)

A **resource** is a real place or program that helps people: a food pantry, shelter,
clinic, shower, or benefits office. Each resource is stored as one record.

Code: `system/models/resources.py`. Sample records: `data/mock/mock_resources.json`.

## Fields

| Field | Required | What it means | Example |
|---|---|---|---|
| `id` | yes | Unique ID: category, a dash, then a number | `food-001` |
| `name` | yes | Name of the place or program | `Sample Community Kitchen` |
| `category` | yes | One of: `food`, `shelter`, `health`, `hygiene`, `benefits`, `other` | `food` |
| `latitude` | yes | North–south position (WGS84). Must be inside San Diego County (32.5 to 33.5) | `32.7157` |
| `longitude` | yes | East–west position (WGS84). Must be inside San Diego County (-117.6 to -116.0) | `-117.1611` |
| `address` | no | Street address | `100 Example St, San Diego, CA` |
| `hours` | no | List of open periods. Each has `day` (`mon`–`sun`), `opens` and `closes` (24-hour time). If `closes` is earlier than `opens`, it is open overnight. An empty list means the hours are unknown. | `{"day": "mon", "opens": "09:00", "closes": "17:00"}` |
| `eligibility` | yes | Who can use it, in plain words | `Adults 18 and older` |
| `source` | yes | Where the information came from (a link or organization name) | `https://example.org/services` |
| `last_verified` | yes | Date someone last checked the information. Cannot be in the future. | `2026-11-20` |

## What makes a record invalid

- A required field is missing or empty
- `id` is not in the `category-number` format
- `category` is not one of the six allowed values
- The location is outside San Diego County
- An open period opens and closes at the same time
- `last_verified` is a future date
- The record has a field that is not in this list

## Sample data

`data/mock/mock_resources.json` holds 12 records. **All of them are made up.** The names,
addresses, hours and links are fake, and the locations are random points in downtown
San Diego. Do not treat them as real services.
