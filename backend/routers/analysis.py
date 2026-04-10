"""
Analysis router — GPX upload, SSE progress, and result retrieval.
"""
from __future__ import annotations

import asyncio
import json
import uuid
from datetime import date

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from core.supabase import get_supabase_admin
from middleware.auth import AuthUser
from middleware.rate_limit import check_analysis_rate_limit
from services.gpx_analyzer import AnalysisParams
from services.job_manager import (
    create_job,
    get_result,
    run_analysis_job,
    sse_generator,
)

router = APIRouter(prefix="/api")

MAX_GPX_SIZE = 50 * 1024 * 1024  # 50MB


@router.post("/analysis/upload")
async def upload_and_analyze(
    user: AuthUser,
    file: UploadFile = File(...),
    stage_name: str = Form(default=""),
    analysis_date: str = Form(default=""),
    start_hour: int = Form(default=11),
    rider_weight: float = Form(default=70.0),
    ftp_wkg: float = Form(default=4.5),
    rider_id: str | None = Form(default=None),
):
    """Upload a GPX file, save to storage, and launch analysis."""
    check_analysis_rate_limit(user.team_id)

    # Validate file
    if not file.filename or not file.filename.lower().endswith(".gpx"):
        raise HTTPException(400, "Only .gpx files are accepted")

    content = await file.read()
    if len(content) > MAX_GPX_SIZE:
        raise HTTPException(400, f"File too large (max {MAX_GPX_SIZE // 1024 // 1024}MB)")

    gpx_content = content.decode("utf-8", errors="replace")

    # Create stage record
    stage_id = str(uuid.uuid4())
    sb = get_supabase_admin()

    # Quick parse for metadata
    import gpxpy
    try:
        gpx = gpxpy.parse(gpx_content)
    except Exception:
        raise HTTPException(400, "Invalid GPX file")

    points = [p for t in gpx.tracks for s in t.segments for p in s.points]
    if len(points) < 10:
        raise HTTPException(400, f"GPX has too few points ({len(points)})")

    # Compute basic metadata
    total_dist = 0.0
    d_pos = 0.0
    from services.gpx_analyzer import _haversine
    for i in range(1, len(points)):
        total_dist += _haversine(
            points[i - 1].latitude, points[i - 1].longitude,
            points[i].latitude, points[i].longitude,
        )
        elev_diff = (points[i].elevation or 0) - (points[i - 1].elevation or 0)
        if elev_diff > 0:
            d_pos += elev_diff

    name = stage_name or (file.filename.replace(".gpx", "").replace(".GPX", "") if file.filename else "Track")

    # Upload GPX to Supabase Storage
    storage_path = f"{user.team_id}/{stage_id}.gpx"
    sb.storage.from_("gpx-files").upload(storage_path, content)

    # Insert stage record
    sb.table("stages").insert({
        "id": stage_id,
        "team_id": user.team_id,
        "name": name,
        "distance_km": round(total_dist, 2),
        "d_pos_m": round(d_pos, 1),
        "points": len(points),
        "gpx_url": storage_path,
        "created_by": user.id,
    }).execute()

    # If rider_id provided, load rider's weight/FTP
    weight = rider_weight
    ftp = ftp_wkg
    if rider_id:
        rider_result = sb.table("riders").select("weight_kg, ftp_wkg").eq(
            "id", rider_id
        ).eq("team_id", user.team_id).single().execute()
        if rider_result.data:
            weight = rider_result.data.get("weight_kg") or weight
            ftp = rider_result.data.get("ftp_wkg") or ftp

    # Create analysis job
    params = AnalysisParams(
        analysis_date=analysis_date or date.today().isoformat(),
        start_hour=start_hour,
        rider_weight_kg=weight,
        ftp_wkg=ftp,
    )

    create_job(stage_id)

    # Get center coordinates for weather
    mid = len(points) // 2
    lat_center = points[mid].latitude
    lon_center = points[mid].longitude

    # Launch async task
    asyncio.create_task(
        run_analysis_job(stage_id, gpx_content, params, lat_center, lon_center)
    )

    return {"stage_id": stage_id}


@router.get("/analysis/sse/{stage_id}")
async def analysis_sse(stage_id: str, user: AuthUser):
    """SSE endpoint for analysis progress."""
    return StreamingResponse(
        sse_generator(stage_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/analysis/data/{stage_id}")
async def get_analysis_data(stage_id: str, user: AuthUser):
    """Get analysis data (all metrics except Plotly figure)."""
    # Check in-memory result first
    result = get_result(stage_id)
    if result:
        return {
            "dists": result.dists,
            "alts": result.alts,
            "lats": result.lats,
            "lons": result.lons,
            "bearings": result.bearings,
            "pends": result.pends,
            "colors_grade": result.colors_grade,
            "colors_wind": result.colors_wind,
            "colors_rain": result.colors_rain,
            "colors_danger": result.colors_danger,
            "colors_surf": result.colors_surf,
            "wind_dirs": result.wind_dirs,
            "rain_km": result.rain_km,
            "surf_map": result.surf_map,
            "roadbook": result.roadbook,
            "tactical_summary": result.tactical_summary,
            "stats": result.stats,
            "idx_staff": result.idx_staff,
            "idx_cursor": result.idx_cursor,
        }

    # Fallback: check Supabase
    sb = get_supabase_admin()
    db_result = sb.table("stage_analyses").select(
        "analysis_json"
    ).eq("stage_id", stage_id).eq("team_id", user.team_id).order(
        "created_at", desc=True
    ).limit(1).execute()

    if db_result.data and db_result.data[0].get("analysis_json"):
        return db_result.data[0]["analysis_json"]

    raise HTTPException(404, "Analysis not found")


@router.get("/analysis/fig/{stage_id}")
async def get_analysis_figure(stage_id: str, user: AuthUser):
    """Get Plotly figure JSON for a stage analysis."""
    result = get_result(stage_id)
    if result:
        return result.fig_json

    # Fallback: check Supabase
    sb = get_supabase_admin()
    db_result = sb.table("stage_analyses").select(
        "fig_json"
    ).eq("stage_id", stage_id).eq("team_id", user.team_id).order(
        "created_at", desc=True
    ).limit(1).execute()

    if db_result.data and db_result.data[0].get("fig_json"):
        return db_result.data[0]["fig_json"]

    raise HTTPException(404, "Analysis figure not found")
