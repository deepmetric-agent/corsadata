"""
Role-based permissions middleware.
Enforces access control per role at the API level.
"""
from __future__ import annotations

from fastapi import Depends, HTTPException

from middleware.auth import CurrentUser, get_current_user

# Permission matrix
# director: full access
# coach: no billing, no team management
# analyst: read-only for races and riders, can run analysis
# rider: only own data
ROLE_PERMISSIONS = {
    "director": {"manage_team", "manage_billing", "crud_riders", "crud_races", "run_analysis", "view_all"},
    "coach": {"crud_riders", "crud_races", "run_analysis", "view_all"},
    "analyst": {"run_analysis", "view_all"},
    "rider": {"view_own"},
}


def require_role(*roles: str):
    """Dependency factory: require the user to have one of the specified roles."""
    async def dependency(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if user.role not in roles:
            raise HTTPException(
                status_code=403,
                detail=f"Insufficient permissions. Required role: {', '.join(roles)}",
            )
        return user
    return Depends(dependency)


def require_permission(permission: str):
    """Dependency factory: require the user to have a specific permission."""
    async def dependency(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        user_perms = ROLE_PERMISSIONS.get(user.role, set())
        if permission not in user_perms:
            raise HTTPException(
                status_code=403,
                detail=f"Insufficient permissions for: {permission}",
            )
        return user
    return Depends(dependency)
