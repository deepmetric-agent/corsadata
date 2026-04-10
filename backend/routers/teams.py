"""
Teams router — Onboarding, invitations, and member management.
"""
from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException

from core.supabase import get_supabase_admin
from middleware.auth import AuthUser
from models.schemas import InvitationCreate, TeamCreate

router = APIRouter(prefix="/api")


@router.post("/teams")
async def create_team(body: TeamCreate, user: AuthUser):
    """Create a new team (onboarding)."""
    sb = get_supabase_admin()

    # Check slug uniqueness
    existing = sb.table("teams").select("id").eq("slug", body.slug).execute()
    if existing.data:
        raise HTTPException(400, "Slug already taken")

    result = sb.table("teams").insert({
        "name": body.name,
        "slug": body.slug,
    }).execute()

    if not result.data:
        raise HTTPException(500, "Failed to create team")

    team_id = result.data[0]["id"]

    # Update user's profile to belong to this team
    sb.table("profiles").update({
        "team_id": team_id,
        "role": "director",
    }).eq("id", user.id).execute()

    return result.data[0]


@router.get("/teams/me")
async def get_my_team(user: AuthUser):
    """Get the current user's team."""
    sb = get_supabase_admin()
    result = sb.table("teams").select("*").eq("id", user.team_id).single().execute()
    if not result.data:
        raise HTTPException(404, "Team not found")
    return result.data


@router.patch("/teams/me")
async def update_team(user: AuthUser, name: str | None = None, logo_url: str | None = None):
    """Update team details."""
    sb = get_supabase_admin()
    data = {}
    if name:
        data["name"] = name
    if logo_url:
        data["logo_url"] = logo_url
    if not data:
        raise HTTPException(400, "No fields to update")

    result = sb.table("teams").update(data).eq("id", user.team_id).execute()
    return result.data[0] if result.data else {}


@router.post("/teams/invite")
async def invite_member(body: InvitationCreate, user: AuthUser):
    """Send an invitation to join the team."""
    sb = get_supabase_admin()

    # Generate secure token
    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    expires_at = (datetime.now(timezone.utc) + timedelta(hours=72)).isoformat()

    sb.table("invitations").insert({
        "team_id": user.team_id,
        "email": body.email,
        "token_hash": token_hash,
        "expires_at": expires_at,
    }).execute()

    # In production, send email with the token link
    # For now, return the token (dev only)
    return {"token": token, "expires_at": expires_at}


@router.post("/teams/accept-invite")
async def accept_invite(token: str):
    """Accept an invitation and link user to team."""
    sb = get_supabase_admin()
    token_hash = hashlib.sha256(token.encode()).hexdigest()

    invitation = sb.table("invitations").select("*").eq(
        "token_hash", token_hash
    ).eq("used", False).single().execute()

    if not invitation.data:
        raise HTTPException(400, "Invalid or already used invitation")

    # Check expiry
    expires_at = datetime.fromisoformat(invitation.data["expires_at"])
    if datetime.now(timezone.utc) > expires_at:
        raise HTTPException(400, "Invitation expired")

    # Mark as used
    sb.table("invitations").update({"used": True}).eq(
        "id", invitation.data["id"]
    ).execute()

    return {"team_id": invitation.data["team_id"], "email": invitation.data["email"]}


@router.get("/teams/members")
async def list_members(user: AuthUser):
    """List all team members."""
    sb = get_supabase_admin()
    result = sb.table("profiles").select("id, full_name, role, avatar_url, created_at").eq(
        "team_id", user.team_id
    ).execute()
    return result.data or []


@router.patch("/teams/members/{member_id}/role")
async def update_member_role(member_id: str, role: str, user: AuthUser):
    """Change a team member's role."""
    valid_roles = {"director", "coach", "analyst", "rider"}
    if role not in valid_roles:
        raise HTTPException(400, f"Invalid role. Must be one of: {valid_roles}")

    sb = get_supabase_admin()
    result = sb.table("profiles").update({"role": role}).eq(
        "id", member_id
    ).eq("team_id", user.team_id).execute()
    return result.data[0] if result.data else {}


@router.delete("/teams/members/{member_id}")
async def remove_member(member_id: str, user: AuthUser):
    """Remove a member from the team."""
    if member_id == user.id:
        raise HTTPException(400, "Cannot remove yourself")

    sb = get_supabase_admin()
    sb.table("profiles").delete().eq(
        "id", member_id
    ).eq("team_id", user.team_id).execute()
    return {"removed": True}
