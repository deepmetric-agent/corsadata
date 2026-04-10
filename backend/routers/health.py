from fastapi import APIRouter

from models.common import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Public health check endpoint."""
    return HealthResponse(status="ok")
