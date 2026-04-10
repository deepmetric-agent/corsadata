from __future__ import annotations

import logging
from dataclasses import dataclass
from functools import lru_cache
from typing import Annotated

from fastapi import Depends, HTTPException, Request
from jose import JWTError, jwt

from core.config import settings
from core.supabase import get_supabase_admin

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CurrentUser:
    id: str
    team_id: str
    role: str  # director | coach | analyst | rider


def _extract_token(request: Request) -> str:
    """Extract JWT from Authorization header or cookie."""
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header[7:]

    token = request.cookies.get("sb-access-token")
    if token:
        return token

    raise HTTPException(status_code=401, detail="Missing authentication token")


@lru_cache(maxsize=256)
def _get_profile(user_id: str) -> tuple[str, str]:
    """Fetch team_id and role from profiles table. Cached for performance."""
    sb = get_supabase_admin()
    result = sb.table("profiles").select("team_id, role").eq("id", user_id).single().execute()
    if not result.data:
        raise HTTPException(status_code=401, detail="User profile not found")
    return result.data["team_id"], result.data["role"]


async def get_current_user(request: Request) -> CurrentUser:
    """FastAPI dependency: verify JWT and return CurrentUser with team_id from DB."""
    token = _extract_token(request)

    try:
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated",
        )
    except JWTError as e:
        logger.warning("JWT verification failed: %s", e)
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_id: str | None = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    try:
        team_id, role = _get_profile(user_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to fetch profile for user %s: %s", user_id, e)
        raise HTTPException(status_code=500, detail="Internal server error")

    return CurrentUser(id=user_id, team_id=team_id, role=role)


# Type alias for dependency injection
AuthUser = Annotated[CurrentUser, Depends(get_current_user)]
