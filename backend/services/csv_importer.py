"""
CSV Importer — Import performance entries from CSV with validation.
Sanitizes Excel formula injection and enforces row limits.
"""
from __future__ import annotations

import csv
import io
from typing import Any

from core.supabase import get_supabase_admin

MAX_ROWS = 10_000
FORMULA_PREFIXES = ("=", "+", "-", "@")


def _sanitize_cell(value: str) -> str:
    """Strip formula prefixes to prevent Excel injection."""
    stripped = value.strip()
    if stripped and stripped[0] in FORMULA_PREFIXES:
        return "'" + stripped  # Prefix with quote to neutralize
    return stripped


def import_csv(content: str, team_id: str) -> dict[str, Any]:
    """
    Parse and import CSV performance data.
    Expected columns: rider_id, date, type, distance_km, duration_min,
                      avg_power_w, normalized_power_w, tss, ftp_tested, notes
    """
    reader = csv.DictReader(io.StringIO(content))
    rows = list(reader)

    if len(rows) > MAX_ROWS:
        return {
            "imported": 0,
            "errors": [{"row": 0, "message": f"Too many rows ({len(rows)}). Max {MAX_ROWS}."}],
        }

    sb = get_supabase_admin()
    imported = 0
    errors: list[dict[str, Any]] = []

    # Get valid rider IDs for this team
    riders_result = sb.table("riders").select("id").eq("team_id", team_id).execute()
    valid_rider_ids = {r["id"] for r in (riders_result.data or [])}

    for i, row in enumerate(rows, start=1):
        try:
            # Sanitize all values
            row = {k: _sanitize_cell(v) for k, v in row.items()}

            rider_id = row.get("rider_id", "").strip()
            if not rider_id:
                errors.append({"row": i, "message": "Missing rider_id"})
                continue

            if rider_id not in valid_rider_ids:
                errors.append({"row": i, "message": f"Invalid rider_id: {rider_id}"})
                continue

            date_str = row.get("date", "").strip()
            if not date_str:
                errors.append({"row": i, "message": "Missing date"})
                continue

            entry: dict[str, Any] = {
                "rider_id": rider_id,
                "team_id": team_id,
                "date": date_str,
            }

            # Optional numeric fields
            for field in ("distance_km", "duration_min", "avg_power_w",
                          "normalized_power_w", "tss", "ftp_tested"):
                val = row.get(field, "").strip()
                if val:
                    try:
                        entry[field] = float(val)
                    except ValueError:
                        errors.append({"row": i, "message": f"Invalid number for {field}: {val}"})
                        continue

            for field in ("type", "notes"):
                val = row.get(field, "").strip()
                if val:
                    entry[field] = val

            sb.table("performance_entries").insert(entry).execute()
            imported += 1

        except Exception as e:
            errors.append({"row": i, "message": str(e)})

    return {"imported": imported, "errors": errors}
