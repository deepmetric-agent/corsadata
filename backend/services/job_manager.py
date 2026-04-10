"""
Async job manager for GPX analysis — asyncio-based queue system.
Replaces Flask's threading approach with native async tasks.
"""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, AsyncGenerator

from services.gpx_analyzer import AnalysisParams, AnalysisResult, analyze_gpx
from services.weather import fetch_weather
from services.surface import fetch_surface_types

logger = logging.getLogger(__name__)

# Active job queues: stage_id -> asyncio.Queue
_job_queues: dict[str, asyncio.Queue[str]] = {}
# Active job results: stage_id -> AnalysisResult
_job_results: dict[str, AnalysisResult] = {}


def create_job(stage_id: str) -> asyncio.Queue[str]:
    """Create a new SSE queue for a job."""
    queue: asyncio.Queue[str] = asyncio.Queue()
    _job_queues[stage_id] = queue
    return queue


def get_queue(stage_id: str) -> asyncio.Queue[str] | None:
    """Get the SSE queue for a job."""
    return _job_queues.get(stage_id)


def get_result(stage_id: str) -> AnalysisResult | None:
    """Get a completed job's result."""
    return _job_results.get(stage_id)


async def run_analysis_job(
    stage_id: str,
    gpx_content: str,
    params: AnalysisParams,
    lat_center: float | None = None,
    lon_center: float | None = None,
) -> None:
    """Run the full analysis pipeline as an async task, emitting SSE events."""
    queue = _job_queues.get(stage_id)
    if not queue:
        return

    try:
        # Emit start
        await _emit(queue, "job_update", {"msg": "Iniciando analisis...", "progress": 5})

        # Fetch weather data
        weather_data = None
        if lat_center is not None and lon_center is not None:
            await _emit(queue, "job_update", {"msg": "Obteniendo datos meteorologicos...", "progress": 15})
            weather_data = await fetch_weather(
                lat_center, lon_center,
                params.analysis_date,
                params.start_hour,
                0,
            )

        # Quick parse to get coordinates for surface fetch
        import gpxpy as gpx_module
        gpx = gpx_module.parse(gpx_content)
        all_points = [p for t in gpx.tracks for s in t.segments for p in s.points]
        lats = [p.latitude for p in all_points]
        lons = [p.longitude for p in all_points]

        # Fetch surface data
        await _emit(queue, "job_update", {"msg": "Obteniendo datos de pavimento...", "progress": 25})
        surface_data = await fetch_surface_types(lats, lons, len(all_points))

        # Run main analysis
        async def progress_cb(msg: str, pct: int):
            # Scale progress: 30-95 range
            scaled = 30 + int(pct * 0.65)
            await _emit(queue, "job_update", {"msg": msg, "progress": scaled})

        result = await analyze_gpx(
            gpx_content,
            params,
            weather_data=weather_data,
            surface_data=surface_data,
            progress_callback=progress_cb,
        )

        # Store result
        _job_results[stage_id] = result

        await _emit(queue, "job_update", {"msg": "Guardando resultados...", "progress": 97})

        # Signal completion
        await _emit(queue, "analysis_ready", {"stage_id": stage_id})

    except Exception as e:
        logger.error("Analysis job failed for %s: %s", stage_id, e, exc_info=True)
        await _emit(queue, "error", {"error": str(e)})
    finally:
        # Clean up queue after a delay (let client receive final events)
        await asyncio.sleep(5)
        _job_queues.pop(stage_id, None)


async def _emit(queue: asyncio.Queue[str], event_type: str, data: dict[str, Any]) -> None:
    """Emit an SSE event to the queue."""
    event = {"type": event_type}
    if event_type == "job_update":
        event["job"] = data
    elif event_type == "error":
        event["error"] = data.get("error", "Unknown error")
    else:
        event.update(data)

    await queue.put(json.dumps(event))


async def sse_generator(stage_id: str) -> AsyncGenerator[str, None]:
    """Generate SSE events from a job queue."""
    queue = get_queue(stage_id)
    if not queue:
        yield f"data: {json.dumps({'type': 'error', 'error': 'Job not found'})}\n\n"
        return

    while True:
        try:
            event_data = await asyncio.wait_for(queue.get(), timeout=30.0)
            yield f"data: {event_data}\n\n"

            # Stop after terminal events
            parsed = json.loads(event_data)
            if parsed.get("type") in ("analysis_ready", "error"):
                break
        except asyncio.TimeoutError:
            # Send keepalive
            yield f"data: {json.dumps({'type': 'keepalive'})}\n\n"
