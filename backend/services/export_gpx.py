"""
GPX Export — Generate GPX file with waypoints.
Compatible with Garmin, Wahoo, RideWithGPS, Komoot.
"""
from __future__ import annotations

from typing import Any

import gpxpy
import gpxpy.gpx


def generate_gpx_with_waypoints(
    stage_name: str,
    waypoints: list[dict[str, Any]],
    analysis_json: dict[str, Any] | None = None,
) -> str:
    """Generate a GPX XML string with waypoints."""
    gpx = gpxpy.gpx.GPX()
    gpx.name = f"{stage_name} — Director Hub PRO"
    gpx.description = f"Waypoints tacticos para {stage_name}"

    # Add waypoints
    for wp in waypoints:
        wpt = gpxpy.gpx.GPXWaypoint(
            latitude=wp.get("lat", 0),
            longitude=wp.get("lon", 0),
            elevation=wp.get("alt"),
            name=wp.get("name", "Waypoint"),
            type_=wp.get("type", ""),
        )
        gpx.waypoints.append(wpt)

    # Optionally add the route as a track
    if analysis_json:
        lats = analysis_json.get("lats", [])
        lons = analysis_json.get("lons", [])
        alts = analysis_json.get("alts", [])

        if lats and lons:
            track = gpxpy.gpx.GPXTrack()
            track.name = stage_name
            segment = gpxpy.gpx.GPXTrackSegment()

            step = max(1, len(lats) // 2000)  # Limit points for file size
            for i in range(0, len(lats), step):
                point = gpxpy.gpx.GPXTrackPoint(
                    latitude=lats[i],
                    longitude=lons[i],
                    elevation=alts[i] if i < len(alts) else None,
                )
                segment.points.append(point)

            track.segments.append(segment)
            gpx.tracks.append(track)

    return gpx.to_xml()
