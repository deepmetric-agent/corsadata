"""
Quota middleware — Enforce plan limits on resource creation.
"""
from __future__ import annotations

from datetime import date, timedelta

from fastapi import HTTPException

from core.supabase import get_supabase_admin

PLAN_LIMITS = {
    "free": {"riders": 10, "analyses_per_month": 5, "members": 2},
    "pro": {"riders": 50, "analyses_per_month": 100, "members": 10},
    "enterprise": {"riders": -1, "analyses_per_month": -1, "members": -1},
}


def _get_team_plan(team_id: str) -> str:
    sb = get_supabase_admin()
    result = sb.table("teams").select("plan").eq("id", team_id).single().execute()
    return result.data["plan"] if result.data else "free"


def check_rider_quota(team_id: str) -> None:
    """Check if team can create more riders."""
    plan = _get_team_plan(team_id)
    limits = PLAN_LIMITS.get(plan, PLAN_LIMITS["free"])
    max_riders = limits["riders"]
    if max_riders == -1:
        return

    sb = get_supabase_admin()
    count = sb.table("riders").select("id", count="exact").eq(
        "team_id", team_id
    ).neq("status", "inactive").execute()
    current = count.count or 0

    if current >= max_riders:
        raise HTTPException(
            402,
            f"Plan '{plan}' limit reached: max {max_riders} riders. Upgrade to add more.",
        )


def check_analysis_quota(team_id: str) -> None:
    """Check if team can run more analyses this month."""
    plan = _get_team_plan(team_id)
    limits = PLAN_LIMITS.get(plan, PLAN_LIMITS["free"])
    max_analyses = limits["analyses_per_month"]
    if max_analyses == -1:
        return

    sb = get_supabase_admin()
    month_start = date.today().replace(day=1).isoformat()
    count = sb.table("stage_analyses").select("id", count="exact").eq(
        "team_id", team_id
    ).gte("created_at", month_start).execute()
    current = count.count or 0

    if current >= max_analyses:
        raise HTTPException(
            402,
            f"Plan '{plan}' limit reached: max {max_analyses} analyses/month. Upgrade to continue.",
        )


def check_member_quota(team_id: str) -> None:
    """Check if team can invite more members."""
    plan = _get_team_plan(team_id)
    limits = PLAN_LIMITS.get(plan, PLAN_LIMITS["free"])
    max_members = limits["members"]
    if max_members == -1:
        return

    sb = get_supabase_admin()
    count = sb.table("profiles").select("id", count="exact").eq(
        "team_id", team_id
    ).execute()
    current = count.count or 0

    if current >= max_members:
        raise HTTPException(
            402,
            f"Plan '{plan}' limit reached: max {max_members} members. Upgrade to invite more.",
        )
