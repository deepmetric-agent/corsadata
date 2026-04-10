from datetime import date as Date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ============================================================
# STAGES
# ============================================================
class StageCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    race_name: Optional[str] = None
    stage_number: Optional[int] = None


class StageResponse(BaseModel):
    id: UUID
    name: str
    race_name: Optional[str] = None
    stage_number: Optional[int] = None
    distance_km: Optional[float] = None
    d_pos_m: Optional[float] = None
    points: Optional[int] = None
    gpx_url: Optional[str] = None
    created_at: str


# ============================================================
# ANALYSIS
# ============================================================
class AnalysisParams(BaseModel):
    date: Optional[Date] = None
    start_hour: int = Field(default=11, ge=0, le=23)
    rider_weight: float = Field(default=70.0, gt=30, lt=200)
    ftp_wkg: float = Field(default=4.5, gt=0, lt=10)
    rider_id: Optional[UUID] = None


class AnalysisResponse(BaseModel):
    stage_id: str


# ============================================================
# RIDERS
# ============================================================
class RiderCreate(BaseModel):
    full_name: str = Field(min_length=1, max_length=200)
    birth_date: Optional[Date] = None
    nationality: Optional[str] = Field(default=None, max_length=3)
    weight_kg: Optional[float] = Field(default=None, gt=0, lt=200)
    height_cm: Optional[float] = Field(default=None, gt=0, lt=250)
    ftp_w: Optional[float] = Field(default=None, gt=0)
    ftp_wkg: Optional[float] = Field(default=None, gt=0, lt=10)
    vo2max: Optional[float] = Field(default=None, gt=0)
    contract_end: Optional[Date] = None
    status: str = Field(default="active", pattern=r"^(active|injured|inactive)$")
    notes: Optional[str] = None


class RiderUpdate(BaseModel):
    full_name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    birth_date: Optional[Date] = None
    nationality: Optional[str] = Field(default=None, max_length=3)
    weight_kg: Optional[float] = Field(default=None, gt=0, lt=200)
    height_cm: Optional[float] = Field(default=None, gt=0, lt=250)
    ftp_w: Optional[float] = Field(default=None, gt=0)
    ftp_wkg: Optional[float] = Field(default=None, gt=0, lt=10)
    vo2max: Optional[float] = Field(default=None, gt=0)
    contract_end: Optional[Date] = None
    status: Optional[str] = Field(default=None, pattern=r"^(active|injured|inactive)$")
    notes: Optional[str] = None


class RiderResponse(BaseModel):
    id: UUID
    full_name: str
    birth_date: Optional[Date] = None
    nationality: Optional[str] = None
    weight_kg: Optional[float] = None
    height_cm: Optional[float] = None
    ftp_w: Optional[float] = None
    ftp_wkg: Optional[float] = None
    vo2max: Optional[float] = None
    contract_end: Optional[Date] = None
    status: str
    notes: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: str


class FTPEntryCreate(BaseModel):
    date: Date
    ftp_w: float = Field(gt=0)
    ftp_wkg: Optional[float] = Field(default=None, gt=0, lt=10)


# ============================================================
# RACES
# ============================================================
class RaceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    start_date: Optional[Date] = None
    end_date: Optional[Date] = None
    category: Optional[str] = None
    country: Optional[str] = Field(default=None, max_length=3)
    status: str = Field(default="upcoming", pattern=r"^(upcoming|ongoing|completed|cancelled)$")


class RaceUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    start_date: Optional[Date] = None
    end_date: Optional[Date] = None
    category: Optional[str] = None
    country: Optional[str] = Field(default=None, max_length=3)
    status: Optional[str] = Field(default=None, pattern=r"^(upcoming|ongoing|completed|cancelled)$")


class RaceEntryCreate(BaseModel):
    rider_id: UUID
    role: Optional[str] = None


class ResultUpdate(BaseModel):
    result: Optional[str] = None


# ============================================================
# PERFORMANCE
# ============================================================
class PerformanceEntryCreate(BaseModel):
    rider_id: UUID
    date: Date
    type: Optional[str] = None
    distance_km: Optional[float] = None
    duration_min: Optional[float] = None
    avg_power_w: Optional[float] = None
    normalized_power_w: Optional[float] = None
    tss: Optional[float] = None
    ftp_tested: Optional[float] = None
    notes: Optional[str] = None


# ============================================================
# WAYPOINTS
# ============================================================
class WaypointCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    type: Optional[str] = None
    km: float
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)
    alt: Optional[float] = None


class WaypointResponse(BaseModel):
    id: UUID
    name: str
    type: Optional[str] = None
    km: float
    lat: float
    lon: float
    alt: Optional[float] = None


# ============================================================
# TEAMS & INVITATIONS
# ============================================================
class TeamCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    slug: str = Field(min_length=1, max_length=50, pattern=r"^[a-z0-9-]+$")


class InvitationCreate(BaseModel):
    email: str = Field(min_length=5, max_length=200)


class InvitationAccept(BaseModel):
    token: str
    full_name: str = Field(min_length=1, max_length=200)
    password: str = Field(min_length=8)
