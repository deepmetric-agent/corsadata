"""
Riders router — Full CRUD for the team roster.
"""
from __future__ import annotations

from fastapi import APIRouter, File, HTTPException, Query, UploadFile

from core.supabase import get_supabase_admin
from middleware.auth import AuthUser
from models.schemas import FTPEntryCreate, RiderCreate, RiderUpdate

router = APIRouter(prefix="/api")

ALLOWED_AVATAR_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_AVATAR_SIZE = 5 * 1024 * 1024  # 5MB


@router.get("/riders")
async def list_riders(
    user: AuthUser,
    status: str | None = Query(default=None),
    nationality: str | None = Query(default=None),
    search: str | None = Query(default=None),
):
    """List riders for the team with optional filters."""
    sb = get_supabase_admin()
    query = sb.table("riders").select("*").eq("team_id", user.team_id)

    if status:
        query = query.eq("status", status)
    if nationality:
        query = query.eq("nationality", nationality)
    if search:
        query = query.ilike("full_name", f"%{search}%")

    result = query.order("full_name").execute()
    return result.data or []


@router.post("/riders")
async def create_rider(body: RiderCreate, user: AuthUser):
    """Create a new rider for the team."""
    sb = get_supabase_admin()
    data = body.model_dump(exclude_none=True)
    data["team_id"] = user.team_id

    result = sb.table("riders").insert(data).execute()
    return result.data[0] if result.data else {}


@router.get("/riders/{rider_id}")
async def get_rider(rider_id: str, user: AuthUser):
    """Get a single rider's full profile."""
    sb = get_supabase_admin()
    result = sb.table("riders").select("*").eq(
        "id", rider_id
    ).eq("team_id", user.team_id).single().execute()

    if not result.data:
        raise HTTPException(404, "Rider not found")

    # Include FTP history
    ftp_history = sb.table("ftp_history").select("*").eq(
        "rider_id", rider_id
    ).eq("team_id", user.team_id).order("date", desc=True).execute()

    rider = result.data
    rider["ftp_history"] = ftp_history.data or []
    return rider


@router.patch("/riders/{rider_id}")
async def update_rider(rider_id: str, body: RiderUpdate, user: AuthUser):
    """Update a rider's fields (partial update)."""
    sb = get_supabase_admin()

    # Verify ownership
    existing = sb.table("riders").select("id").eq(
        "id", rider_id
    ).eq("team_id", user.team_id).single().execute()
    if not existing.data:
        raise HTTPException(404, "Rider not found")

    data = body.model_dump(exclude_none=True)
    if not data:
        raise HTTPException(400, "No fields to update")

    result = sb.table("riders").update(data).eq(
        "id", rider_id
    ).eq("team_id", user.team_id).execute()
    return result.data[0] if result.data else {}


@router.delete("/riders/{rider_id}")
async def archive_rider(rider_id: str, user: AuthUser):
    """Archive a rider (logical delete — sets status to 'inactive')."""
    sb = get_supabase_admin()

    existing = sb.table("riders").select("id").eq(
        "id", rider_id
    ).eq("team_id", user.team_id).single().execute()
    if not existing.data:
        raise HTTPException(404, "Rider not found")

    sb.table("riders").update({"status": "inactive"}).eq(
        "id", rider_id
    ).eq("team_id", user.team_id).execute()
    return {"archived": True}


@router.post("/riders/{rider_id}/avatar")
async def upload_avatar(rider_id: str, user: AuthUser, file: UploadFile = File(...)):
    """Upload a rider's avatar photo."""
    # Verify ownership
    sb = get_supabase_admin()
    existing = sb.table("riders").select("id").eq(
        "id", rider_id
    ).eq("team_id", user.team_id).single().execute()
    if not existing.data:
        raise HTTPException(404, "Rider not found")

    # Validate file type
    if file.content_type not in ALLOWED_AVATAR_TYPES:
        raise HTTPException(422, f"Invalid image type. Allowed: {', '.join(ALLOWED_AVATAR_TYPES)}")

    content = await file.read()
    if len(content) > MAX_AVATAR_SIZE:
        raise HTTPException(400, f"Image too large (max {MAX_AVATAR_SIZE // 1024 // 1024}MB)")

    ext = file.filename.rsplit(".", 1)[-1] if file.filename else "jpg"
    storage_path = f"{user.team_id}/{rider_id}.{ext}"

    # Upload (upsert)
    try:
        sb.storage.from_("avatars").remove([storage_path])
    except Exception:
        pass
    sb.storage.from_("avatars").upload(storage_path, content)

    # Get public URL
    public_url = sb.storage.from_("avatars").get_public_url(storage_path)

    # Update rider record
    sb.table("riders").update({"avatar_url": public_url}).eq(
        "id", rider_id
    ).eq("team_id", user.team_id).execute()

    return {"avatar_url": public_url}


@router.get("/riders/{rider_id}/analyses")
async def get_rider_analyses(rider_id: str, user: AuthUser):
    """List analyses linked to a rider."""
    sb = get_supabase_admin()
    result = sb.table("stage_analyses").select(
        "id, stage_id, analysis_date, stats, created_at"
    ).eq("rider_id", rider_id).eq("team_id", user.team_id).order(
        "created_at", desc=True
    ).execute()
    return result.data or []


@router.post("/riders/{rider_id}/ftp-entry")
async def add_ftp_entry(rider_id: str, body: FTPEntryCreate, user: AuthUser):
    """Register a new FTP measurement."""
    sb = get_supabase_admin()

    existing = sb.table("riders").select("id, weight_kg").eq(
        "id", rider_id
    ).eq("team_id", user.team_id).single().execute()
    if not existing.data:
        raise HTTPException(404, "Rider not found")

    # Calculate ftp_wkg if weight is available and ftp_wkg not provided
    ftp_wkg = body.ftp_wkg
    if not ftp_wkg and existing.data.get("weight_kg"):
        ftp_wkg = round(body.ftp_w / existing.data["weight_kg"], 2)

    # Insert history entry
    sb.table("ftp_history").insert({
        "rider_id": rider_id,
        "team_id": user.team_id,
        "date": body.date.isoformat(),
        "ftp_w": body.ftp_w,
        "ftp_wkg": ftp_wkg,
    }).execute()

    # Update rider's current FTP
    sb.table("riders").update({
        "ftp_w": body.ftp_w,
        "ftp_wkg": ftp_wkg,
    }).eq("id", rider_id).eq("team_id", user.team_id).execute()

    return {"ftp_w": body.ftp_w, "ftp_wkg": ftp_wkg}
