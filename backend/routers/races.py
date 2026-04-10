"""
Races router — CRUD for races, entries, and stage linking.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from core.supabase import get_supabase_admin
from middleware.auth import AuthUser
from models.schemas import RaceCreate, RaceEntryCreate, RaceUpdate, ResultUpdate

router = APIRouter(prefix="/api")


@router.get("/races")
async def list_races(
    user: AuthUser,
    status: str | None = Query(default=None),
):
    """List all races for the team."""
    sb = get_supabase_admin()
    query = sb.table("races").select("*").eq("team_id", user.team_id)
    if status:
        query = query.eq("status", status)
    result = query.order("start_date", desc=True).execute()
    return result.data or []


@router.post("/races")
async def create_race(body: RaceCreate, user: AuthUser):
    """Create a new race."""
    sb = get_supabase_admin()
    data = body.model_dump(exclude_none=True)
    data["team_id"] = user.team_id
    # Serialize dates
    for key in ("start_date", "end_date"):
        if key in data and data[key]:
            data[key] = data[key].isoformat()
    result = sb.table("races").insert(data).execute()
    return result.data[0] if result.data else {}


@router.get("/races/{race_id}")
async def get_race(race_id: str, user: AuthUser):
    """Get a single race with entries and stages."""
    sb = get_supabase_admin()
    race = sb.table("races").select("*").eq(
        "id", race_id
    ).eq("team_id", user.team_id).single().execute()
    if not race.data:
        raise HTTPException(404, "Race not found")

    entries = sb.table("race_entries").select(
        "*, riders(full_name, nationality, status)"
    ).eq("race_id", race_id).eq("team_id", user.team_id).execute()

    linked_stages = sb.table("stages").select("*").eq(
        "race_id", race_id
    ).eq("team_id", user.team_id).execute()

    result = race.data
    result["entries"] = entries.data or []
    result["stages"] = linked_stages.data or []
    return result


@router.patch("/races/{race_id}")
async def update_race(race_id: str, body: RaceUpdate, user: AuthUser):
    """Update a race."""
    sb = get_supabase_admin()
    existing = sb.table("races").select("id").eq(
        "id", race_id
    ).eq("team_id", user.team_id).single().execute()
    if not existing.data:
        raise HTTPException(404, "Race not found")

    data = body.model_dump(exclude_none=True)
    for key in ("start_date", "end_date"):
        if key in data and data[key]:
            data[key] = data[key].isoformat()
    result = sb.table("races").update(data).eq(
        "id", race_id
    ).eq("team_id", user.team_id).execute()
    return result.data[0] if result.data else {}


@router.delete("/races/{race_id}")
async def delete_race(race_id: str, user: AuthUser):
    """Delete a race."""
    sb = get_supabase_admin()
    existing = sb.table("races").select("id").eq(
        "id", race_id
    ).eq("team_id", user.team_id).single().execute()
    if not existing.data:
        raise HTTPException(404, "Race not found")

    sb.table("races").delete().eq("id", race_id).eq("team_id", user.team_id).execute()
    return {"deleted": True}


@router.post("/races/{race_id}/entries")
async def add_race_entry(race_id: str, body: RaceEntryCreate, user: AuthUser):
    """Assign a rider to a race with a role."""
    sb = get_supabase_admin()

    # Verify race and rider belong to the same team
    race = sb.table("races").select("id").eq(
        "id", race_id
    ).eq("team_id", user.team_id).single().execute()
    if not race.data:
        raise HTTPException(404, "Race not found")

    rider = sb.table("riders").select("id").eq(
        "id", str(body.rider_id)
    ).eq("team_id", user.team_id).single().execute()
    if not rider.data:
        raise HTTPException(403, "Rider not in your team")

    result = sb.table("race_entries").insert({
        "race_id": race_id,
        "rider_id": str(body.rider_id),
        "team_id": user.team_id,
        "role": body.role,
    }).execute()
    return result.data[0] if result.data else {}


@router.delete("/races/{race_id}/entries/{entry_id}")
async def remove_race_entry(race_id: str, entry_id: str, user: AuthUser):
    """Remove a rider from a race."""
    sb = get_supabase_admin()
    sb.table("race_entries").delete().eq(
        "id", entry_id
    ).eq("team_id", user.team_id).execute()
    return {"deleted": True}


@router.patch("/races/{race_id}/entries/{entry_id}/result")
async def update_result(race_id: str, entry_id: str, body: ResultUpdate, user: AuthUser):
    """Record post-race result for an entry."""
    sb = get_supabase_admin()
    result = sb.table("race_entries").update(
        {"result": body.result}
    ).eq("id", entry_id).eq("team_id", user.team_id).execute()
    return result.data[0] if result.data else {}


@router.get("/races/{race_id}/stages")
async def get_race_stages(race_id: str, user: AuthUser):
    """List stages linked to a race."""
    sb = get_supabase_admin()
    result = sb.table("stages").select("*").eq(
        "race_id", race_id
    ).eq("team_id", user.team_id).execute()
    return result.data or []


@router.post("/races/{race_id}/stages/{stage_id}")
async def link_stage_to_race(race_id: str, stage_id: str, user: AuthUser):
    """Link an analyzed stage to a race."""
    sb = get_supabase_admin()

    # Verify both belong to the team
    race = sb.table("races").select("id").eq(
        "id", race_id
    ).eq("team_id", user.team_id).single().execute()
    if not race.data:
        raise HTTPException(404, "Race not found")

    stage = sb.table("stages").select("id").eq(
        "id", stage_id
    ).eq("team_id", user.team_id).single().execute()
    if not stage.data:
        raise HTTPException(403, "Stage not in your team")

    sb.table("stages").update({"race_id": race_id}).eq(
        "id", stage_id
    ).eq("team_id", user.team_id).execute()
    return {"linked": True}
