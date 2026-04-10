"""
Surface service — OpenRouteService for road surface types.
Falls back to 'asphalt' if ORS is unavailable.
"""
from __future__ import annotations

import logging
from typing import Any

import httpx

from core.config import settings

logger = logging.getLogger(__name__)

ORS_BASE = "https://api.openrouteservice.org"


async def fetch_surface_types(
    lats: list[float],
    lons: list[float],
    num_points: int,
) -> list[str]:
    """
    Fetch surface types for route points.
    Returns a list of surface type strings aligned to the input points.
    Falls back to all 'asphalt' on failure.
    """
    if not settings.ORS_KEY:
        logger.info("No ORS key configured, using asphalt fallback")
        return ["asphalt"] * num_points

    try:
        return await _fetch_ors(lats, lons, num_points)
    except Exception as e:
        logger.warning("ORS surface fetch failed, using asphalt fallback: %s", e)
        return ["asphalt"] * num_points


async def _fetch_ors(
    lats: list[float],
    lons: list[float],
    num_points: int,
) -> list[str]:
    """Fetch surface info from OpenRouteService."""
    # Sample route points (ORS has a limit on coordinate count)
    step = max(1, len(lats) // 50)
    coords = [[lons[i], lats[i]] for i in range(0, len(lats), step)]

    if len(coords) < 2:
        return ["asphalt"] * num_points

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(
            f"{ORS_BASE}/v2/directions/cycling-road/json",
            headers={
                "Authorization": settings.ORS_KEY,
                "Content-Type": "application/json",
            },
            json={
                "coordinates": coords,
                "extra_info": ["surface"],
            },
        )
        resp.raise_for_status()
        data = resp.json()

    return _parse_surface_response(data, num_points)


def _parse_surface_response(data: dict[str, Any], num_points: int) -> list[str]:
    """Parse ORS response into surface type per point."""
    SURFACE_MAP = {
        0: "asphalt",
        1: "asphalt",
        2: "concrete",
        3: "cobblestone",
        4: "compacted",
        5: "gravel",
        6: "dirt",
        7: "grass",
        8: "sand",
        9: "unpaved",
    }

    routes = data.get("routes", [])
    if not routes:
        return ["asphalt"] * num_points

    extras = routes[0].get("extras", {})
    surface_info = extras.get("surface", {}).get("values", [])

    if not surface_info:
        return ["asphalt"] * num_points

    # Build surface array from ORS segments
    result: list[str] = []
    for segment in surface_info:
        start_idx, end_idx, surface_code = segment
        surface_type = SURFACE_MAP.get(surface_code, "asphalt")
        count = end_idx - start_idx
        result.extend([surface_type] * count)

    # Pad or trim to match num_points
    while len(result) < num_points:
        result.append(result[-1] if result else "asphalt")
    return result[:num_points]
