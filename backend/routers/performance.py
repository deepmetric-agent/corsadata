"""
Performance router — CRUD for performance entries and CSV import.
"""
from __future__ import annotations

from fastapi import APIRouter, File, HTTPException, Query, UploadFile

from core.supabase import get_supabase_admin
from middleware.auth import AuthUser
from models.schemas import PerformanceEntryCreate
from services.csv_importer import import_csv

router = APIRouter(prefix="/api")


@router.get("/performance")
async def list_performance(
    user: AuthUser,
    rider_id: str | None = Query(default=None),
    from_date: str | None = Query(default=None, alias="from"),
    to_date: str | None = Query(default=None, alias="to"),
):
    """List performance entries with optional filters."""
    sb = get_supabase_admin()
    query = sb.table("performance_entries").select("*").eq("team_id", user.team_id)

    if rider_id:
        query = query.eq("rider_id", rider_id)
    if from_date:
        query = query.gte("date", from_date)
    if to_date:
        query = query.lte("date", to_date)

    result = query.order("date", desc=True).execute()
    return result.data or []


@router.post("/performance")
async def create_performance(body: PerformanceEntryCreate, user: AuthUser):
    """Create a performance entry."""
    sb = get_supabase_admin()

    # Verify rider belongs to team
    rider = sb.table("riders").select("id").eq(
        "id", str(body.rider_id)
    ).eq("team_id", user.team_id).single().execute()
    if not rider.data:
        raise HTTPException(403, "Rider not in your team")

    data = body.model_dump(exclude_none=True)
    data["team_id"] = user.team_id
    data["rider_id"] = str(body.rider_id)
    data["date"] = body.date.isoformat()

    result = sb.table("performance_entries").insert(data).execute()
    return result.data[0] if result.data else {}


@router.post("/performance/import")
async def import_performance_csv(user: AuthUser, file: UploadFile = File(...)):
    """Import performance entries from CSV."""
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:  # 10MB limit
        raise HTTPException(400, "File too large")

    text = content.decode("utf-8", errors="replace")
    result = import_csv(text, user.team_id)
    return result
