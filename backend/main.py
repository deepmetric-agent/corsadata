import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from routers import health, analysis, stages, waypoints, exports, riders, races, performance, dashboard, teams, billing

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if not settings.is_production else logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

# Create FastAPI app
app = FastAPI(
    title="Director Hub PRO API",
    version="0.1.0",
    docs_url="/docs" if not settings.is_production else None,
    redoc_url=None,
)

# CORS — only allow the frontend domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(analysis.router, tags=["analysis"])
app.include_router(stages.router, tags=["stages"])
app.include_router(waypoints.router, tags=["waypoints"])
app.include_router(exports.router, tags=["exports"])
app.include_router(riders.router, tags=["riders"])
app.include_router(races.router, tags=["races"])
app.include_router(performance.router, tags=["performance"])
app.include_router(dashboard.router, tags=["dashboard"])
app.include_router(teams.router, tags=["teams"])
app.include_router(billing.router, tags=["billing"])
