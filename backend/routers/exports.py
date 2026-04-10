"""
Export router — GPX and PDF export of analyses.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from core.supabase import get_supabase_admin
from middleware.auth import AuthUser
from services.export_gpx import generate_gpx_with_waypoints
from services.export_pdf import generate_pdf_report

router = APIRouter(prefix="/api")


@router.get("/analysis/{analysis_id}/export/gpx")
async def export_gpx(analysis_id: str, user: AuthUser):
    """Export analysis waypoints as a GPX file."""
    sb = get_supabase_admin()

    # Get analysis
    analysis = sb.table("stage_analyses").select(
        "id, stage_id, analysis_json"
    ).eq("id", analysis_id).eq("team_id", user.team_id).single().execute()

    if not analysis.data:
        raise HTTPException(404, "Analysis not found")

    # Get waypoints
    waypoints = sb.table("waypoints").select("*").eq(
        "analysis_id", analysis_id
    ).eq("team_id", user.team_id).order("km").execute()

    # Get stage name
    stage = sb.table("stages").select("name").eq(
        "id", analysis.data["stage_id"]
    ).single().execute()
    stage_name = stage.data["name"] if stage.data else "Track"

    gpx_xml = generate_gpx_with_waypoints(
        stage_name=stage_name,
        waypoints=waypoints.data or [],
        analysis_json=analysis.data.get("analysis_json"),
    )

    return Response(
        content=gpx_xml,
        media_type="application/gpx+xml",
        headers={"Content-Disposition": f'attachment; filename="{stage_name}_waypoints.gpx"'},
    )


@router.get("/analysis/{analysis_id}/export/pdf")
async def export_pdf(analysis_id: str, user: AuthUser):
    """Export analysis as a PDF report with roadbook and stats."""
    sb = get_supabase_admin()

    analysis = sb.table("stage_analyses").select(
        "id, stage_id, analysis_json, roadbook, stats"
    ).eq("id", analysis_id).eq("team_id", user.team_id).single().execute()

    if not analysis.data:
        raise HTTPException(404, "Analysis not found")

    stage = sb.table("stages").select("name, distance_km, d_pos_m").eq(
        "id", analysis.data["stage_id"]
    ).single().execute()

    waypoints = sb.table("waypoints").select("*").eq(
        "analysis_id", analysis_id
    ).eq("team_id", user.team_id).order("km").execute()

    stage_name = stage.data["name"] if stage.data else "Track"

    pdf_bytes = generate_pdf_report(
        stage_name=stage_name,
        stage_data=stage.data or {},
        stats=analysis.data.get("stats") or {},
        roadbook=analysis.data.get("roadbook") or [],
        waypoints=waypoints.data or [],
    )

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{stage_name}_report.pdf"'},
    )
