"""
Waypoints router — CRUD for waypoints attached to analyses.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from core.supabase import get_supabase_admin
from middleware.auth import AuthUser
from models.schemas import WaypointCreate

router = APIRouter(prefix="/api")


@router.post("/waypoints")
async def create_waypoint(
    body: WaypointCreate,
    user: AuthUser,
    analysis_id: str = "",
):
    """Add a waypoint to an analysis."""
    if not analysis_id:
        raise HTTPException(400, "analysis_id is required")

    sb = get_supabase_admin()

    # Verify analysis belongs to user's team
    analysis = sb.table("stage_analyses").select("id").eq(
        "id", analysis_id
    ).eq("team_id", user.team_id).single().execute()

    if not analysis.data:
        raise HTTPException(404, "Analysis not found")

    result = sb.table("waypoints").insert({
        "analysis_id": analysis_id,
        "team_id": user.team_id,
        "name": body.name,
        "type": body.type,
        "km": body.km,
        "lat": body.lat,
        "lon": body.lon,
        "alt": body.alt,
    }).execute()

    return result.data[0] if result.data else {}


@router.get("/waypoints/{analysis_id}")
async def list_waypoints(analysis_id: str, user: AuthUser):
    """List all waypoints for an analysis."""
    sb = get_supabase_admin()
    result = sb.table("waypoints").select("*").eq(
        "analysis_id", analysis_id
    ).eq("team_id", user.team_id).order("km").execute()
    return result.data or []


@router.delete("/waypoints/{waypoint_id}")
async def delete_waypoint(waypoint_id: str, user: AuthUser):
    """Delete a waypoint."""
    sb = get_supabase_admin()

    wp = sb.table("waypoints").select("id").eq(
        "id", waypoint_id
    ).eq("team_id", user.team_id).single().execute()

    if not wp.data:
        raise HTTPException(404, "Waypoint not found")

    sb.table("waypoints").delete().eq("id", waypoint_id).eq("team_id", user.team_id).execute()
    return {"deleted": True}
