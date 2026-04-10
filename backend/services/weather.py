"""
Weather service — Tomorrow.io + Open-Meteo fallback.
Fetches wind and precipitation data for a route's coordinates.
"""
from __future__ import annotations

import logging
from typing import Any

import httpx

from core.config import settings

logger = logging.getLogger(__name__)

TOMORROW_IO_URL = "https://api.tomorrow.io/v4/timelines"
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


async def fetch_weather(
    lat: float,
    lon: float,
    date: str,
    start_hour: int,
    num_points: int,
) -> dict[str, Any] | None:
    """
    Fetch weather data for a specific location and time.
    Returns dict with wind_speed (km/h), wind_direction (degrees), rain (mm/h).
    Falls back to Open-Meteo if Tomorrow.io fails.
    """
    # Try Tomorrow.io first
    if settings.TOMORROW_IO_KEY:
        try:
            data = await _fetch_tomorrow_io(lat, lon, date, start_hour)
            if data:
                return {
                    "wind_speed": data.get("windSpeed", 0),
                    "wind_direction": data.get("windDirection", 0),
                    "rain": data.get("precipitationIntensity", 0),
                }
        except Exception as e:
            logger.warning("Tomorrow.io failed, falling back to Open-Meteo: %s", e)

    # Fallback: Open-Meteo (free, no API key required)
    try:
        data = await _fetch_open_meteo(lat, lon, date, start_hour)
        if data:
            return data
    except Exception as e:
        logger.warning("Open-Meteo also failed: %s", e)

    return None


async def _fetch_tomorrow_io(
    lat: float, lon: float, date: str, hour: int
) -> dict[str, Any] | None:
    """Fetch from Tomorrow.io Timelines API."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(
            TOMORROW_IO_URL,
            params={
                "location": f"{lat},{lon}",
                "fields": "windSpeed,windDirection,precipitationIntensity,temperature",
                "timesteps": "1h",
                "startTime": f"{date}T{hour:02d}:00:00Z",
                "endTime": f"{date}T{min(hour + 6, 23):02d}:00:00Z",
                "apikey": settings.TOMORROW_IO_KEY,
            },
        )
        resp.raise_for_status()
        result = resp.json()

        timelines = result.get("data", {}).get("timelines", [])
        if timelines and timelines[0].get("intervals"):
            # Average across the race window
            intervals = timelines[0]["intervals"]
            values = [i["values"] for i in intervals]
            avg = {}
            for key in ["windSpeed", "windDirection", "precipitationIntensity"]:
                vals = [v.get(key, 0) for v in values]
                avg[key] = sum(vals) / len(vals) if vals else 0
            return avg

    return None


async def _fetch_open_meteo(
    lat: float, lon: float, date: str, hour: int
) -> dict[str, Any] | None:
    """Fetch from Open-Meteo free API."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(
            OPEN_METEO_URL,
            params={
                "latitude": lat,
                "longitude": lon,
                "hourly": "wind_speed_10m,wind_direction_10m,precipitation",
                "start_date": date,
                "end_date": date,
            },
        )
        resp.raise_for_status()
        result = resp.json()

        hourly = result.get("hourly", {})
        times = hourly.get("time", [])
        wind_speeds = hourly.get("wind_speed_10m", [])
        wind_dirs = hourly.get("wind_direction_10m", [])
        precips = hourly.get("precipitation", [])

        if not times:
            return None

        # Get values around the start hour (average 6h window)
        start = max(0, hour)
        end = min(len(times), hour + 6)

        avg_ws = sum(wind_speeds[start:end]) / max(1, end - start) if wind_speeds else 0
        avg_wd = sum(wind_dirs[start:end]) / max(1, end - start) if wind_dirs else 0
        avg_rain = sum(precips[start:end]) / max(1, end - start) if precips else 0

        return {
            "wind_speed": round(avg_ws, 1),
            "wind_direction": round(avg_wd, 1),
            "rain": round(avg_rain, 2),
        }
