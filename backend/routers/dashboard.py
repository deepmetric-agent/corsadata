"""
Dashboard router — KPIs and alerts for the team.
"""
from __future__ import annotations

from datetime import date, timedelta

from fastapi import APIRouter

from core.supabase import get_supabase_admin
from middleware.auth import AuthUser

router = APIRouter(prefix="/api")


@router.get("/dashboard/kpis")
async def get_kpis(user: AuthUser):
    """Get team KPIs for the dashboard."""
    sb = get_supabase_admin()

    # Count riders by status
    riders = sb.table("riders").select("status").eq("team_id", user.team_id).execute()
    all_riders = riders.data or []
    active = sum(1 for r in all_riders if r["status"] == "active")
    injured = sum(1 for r in all_riders if r["status"] == "injured")
    inactive = sum(1 for r in all_riders if r["status"] == "inactive")

    # Upcoming races
    today = date.today().isoformat()
    upcoming = sb.table("races").select("id").eq(
        "team_id", user.team_id
    ).eq("status", "upcoming").gte("start_date", today).execute()

    # Recent analyses (last 30 days)
    thirty_days_ago = (date.today() - timedelta(days=30)).isoformat()
    analyses = sb.table("stage_analyses").select("id").eq(
        "team_id", user.team_id
    ).gte("created_at", thirty_days_ago).execute()

    # Total stages
    stages_count = sb.table("stages").select("id").eq("team_id", user.team_id).execute()

    return {
        "riders": {
            "total": len(all_riders),
            "active": active,
            "injured": injured,
            "inactive": inactive,
        },
        "upcoming_races": len(upcoming.data or []),
        "recent_analyses": len(analyses.data or []),
        "total_stages": len(stages_count.data or []),
    }


@router.get("/dashboard/alerts")
async def get_alerts(user: AuthUser):
    """Get active alerts for the dashboard."""
    sb = get_supabase_admin()
    alerts = []

    # Riders with outdated FTP (>30 days)
    riders = sb.table("riders").select(
        "id, full_name, ftp_w"
    ).eq("team_id", user.team_id).eq("status", "active").execute()

    thirty_days_ago = (date.today() - timedelta(days=30)).isoformat()
    for rider in (riders.data or []):
        recent_ftp = sb.table("ftp_history").select("id").eq(
            "rider_id", rider["id"]
        ).gte("date", thirty_days_ago).limit(1).execute()

        if not recent_ftp.data:
            alerts.append({
                "type": "ftp_outdated",
                "rider_id": rider["id"],
                "rider_name": rider["full_name"],
                "message": f"FTP de {rider['full_name']} sin actualizar en >30 dias",
            })

    # Expiring contracts (<90 days)
    ninety_days = (date.today() + timedelta(days=90)).isoformat()
    today = date.today().isoformat()
    expiring = sb.table("riders").select(
        "id, full_name, contract_end"
    ).eq("team_id", user.team_id).eq(
        "status", "active"
    ).lte("contract_end", ninety_days).gte("contract_end", today).execute()

    for rider in (expiring.data or []):
        alerts.append({
            "type": "contract_expiring",
            "rider_id": rider["id"],
            "rider_name": rider["full_name"],
            "message": f"Contrato de {rider['full_name']} expira el {rider['contract_end']}",
        })

    return alerts
