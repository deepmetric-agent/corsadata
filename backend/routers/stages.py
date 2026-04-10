"""
Stages router — CRUD for the stage library.
"""
from __future__ import annotations

import asyncio
import uuid
from datetime import date

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from core.supabase import get_supabase_admin
from middleware.auth import AuthUser
from middleware.rate_limit import check_analysis_rate_limit
from services.gpx_analyzer import AnalysisParams, _haversine
from services.job_manager import create_job, run_analysis_job

router = APIRouter(prefix="/api")


@router.get("/stages")
async def list_stages(user: AuthUser):
    """List all stages for the authenticated team."""
    sb = get_supabase_admin()
    result = sb.table("stages").select("*").eq(
        "team_id", user.team_id
    ).order("created_at", desc=True).execute()
    return result.data or []


@router.post("/stages/save")
async def save_stage(
    user: AuthUser,
    file: UploadFile = File(...),
    name: str = Form(default=""),
):
    """Save a GPX to the stage library without running analysis."""
    if not file.filename or not file.filename.lower().endswith(".gpx"):
        raise HTTPException(400, "Only .gpx files are accepted")

    content = await file.read()
    gpx_content = content.decode("utf-8", errors="replace")

    import gpxpy
    try:
        gpx = gpxpy.parse(gpx_content)
    except Exception:
        raise HTTPException(400, "Invalid GPX file")

    points = [p for t in gpx.tracks for s in t.segments for p in s.points]
    if len(points) < 10:
        raise HTTPException(400, f"GPX has too few points ({len(points)})")

    total_dist = 0.0
    d_pos = 0.0
    for i in range(1, len(points)):
        total_dist += _haversine(
            points[i - 1].latitude, points[i - 1].longitude,
            points[i].latitude, points[i].longitude,
        )
        elev_diff = (points[i].elevation or 0) - (points[i - 1].elevation or 0)
        if elev_diff > 0:
            d_pos += elev_diff

    stage_id = str(uuid.uuid4())
    stage_name = name or (file.filename.replace(".gpx", "").replace(".GPX", "") if file.filename else "Track")

    sb = get_supabase_admin()
    storage_path = f"{user.team_id}/{stage_id}.gpx"
    sb.storage.from_("gpx-files").upload(storage_path, content)

    sb.table("stages").insert({
        "id": stage_id,
        "team_id": user.team_id,
        "name": stage_name,
        "distance_km": round(total_dist, 2),
        "d_pos_m": round(d_pos, 1),
        "points": len(points),
        "gpx_url": storage_path,
        "created_by": user.id,
    }).execute()

    return {"id": stage_id, "name": stage_name}


@router.post("/stages/{stage_id}/analyze")
async def analyze_saved_stage(
    stage_id: str,
    user: AuthUser,
    analysis_date: str = Form(default=""),
    start_hour: int = Form(default=11),
    rider_weight: float = Form(default=70.0),
    ftp_wkg: float = Form(default=4.5),
    rider_id: str | None = Form(default=None),
):
    """Launch analysis on a stage from the library."""
    check_analysis_rate_limit(user.team_id)

    sb = get_supabase_admin()
    stage = sb.table("stages").select("*").eq(
        "id", stage_id
    ).eq("team_id", user.team_id).single().execute()

    if not stage.data:
        raise HTTPException(404, "Stage not found")

    gpx_url = stage.data.get("gpx_url")
    if not gpx_url:
        raise HTTPException(400, "Stage has no GPX file")

    # Download GPX from storage
    gpx_bytes = sb.storage.from_("gpx-files").download(gpx_url)
    gpx_content = gpx_bytes.decode("utf-8", errors="replace")

    # Load rider data if provided
    weight = rider_weight
    ftp = ftp_wkg
    if rider_id:
        rider_result = sb.table("riders").select("weight_kg, ftp_wkg").eq(
            "id", rider_id
        ).eq("team_id", user.team_id).single().execute()
        if rider_result.data:
            weight = rider_result.data.get("weight_kg") or weight
            ftp = rider_result.data.get("ftp_wkg") or ftp

    params = AnalysisParams(
        analysis_date=analysis_date or date.today().isoformat(),
        start_hour=start_hour,
        rider_weight_kg=weight,
        ftp_wkg=ftp,
    )

    create_job(stage_id)

    # Get center coords
    import gpxpy as gpx_module
    gpx = gpx_module.parse(gpx_content)
    all_pts = [p for t in gpx.tracks for s in t.segments for p in s.points]
    mid = len(all_pts) // 2
    lat_c = all_pts[mid].latitude if all_pts else None
    lon_c = all_pts[mid].longitude if all_pts else None

    asyncio.create_task(run_analysis_job(stage_id, gpx_content, params, lat_c, lon_c))

    return {"stage_id": stage_id}


@router.delete("/stages/{stage_id}")
async def delete_stage(stage_id: str, user: AuthUser):
    """Delete a stage and its GPX file from storage."""
    sb = get_supabase_admin()

    stage = sb.table("stages").select("gpx_url").eq(
        "id", stage_id
    ).eq("team_id", user.team_id).single().execute()

    if not stage.data:
        raise HTTPException(404, "Stage not found")

    # Delete from storage
    if stage.data.get("gpx_url"):
        try:
            sb.storage.from_("gpx-files").remove([stage.data["gpx_url"]])
        except Exception:
            pass  # Non-critical if storage delete fails

    # Delete from DB (cascades to stage_analyses and waypoints)
    sb.table("stages").delete().eq("id", stage_id).eq("team_id", user.team_id).execute()

    return {"deleted": True}
