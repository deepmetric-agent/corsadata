"""
GPX Analysis Pipeline — Core analysis engine.
Migrated from Flask monolith. Produces the same data structure consumed by the frontend.
"""
from __future__ import annotations

import asyncio
import math
from dataclasses import dataclass, field
from typing import Any

import gpxpy
import numpy as np
import plotly.graph_objects as go


@dataclass
class AnalysisParams:
    analysis_date: str = ""
    start_hour: int = 11
    rider_weight_kg: float = 70.0
    ftp_wkg: float = 4.5


@dataclass
class AnalysisResult:
    """Complete analysis output matching the frontend AnalysisData interface."""
    dists: list[float] = field(default_factory=list)
    alts: list[float] = field(default_factory=list)
    lats: list[float] = field(default_factory=list)
    lons: list[float] = field(default_factory=list)
    bearings: list[float] = field(default_factory=list)
    pends: list[float] = field(default_factory=list)
    colors_grade: list[str] = field(default_factory=list)
    colors_wind: list[str] = field(default_factory=list)
    colors_rain: list[str] = field(default_factory=list)
    colors_danger: list[str] = field(default_factory=list)
    colors_surf: list[str] = field(default_factory=list)
    wind_dirs: list[str] = field(default_factory=list)
    rain_km: list[float] = field(default_factory=list)
    surf_map: list[str] = field(default_factory=list)
    roadbook: list[dict[str, Any]] = field(default_factory=list)
    tactical_summary: dict[str, str] = field(default_factory=dict)
    stats: dict[str, Any] = field(default_factory=dict)
    fig_json: dict[str, Any] = field(default_factory=dict)
    idx_staff: int = -1
    idx_cursor: int = -1


# ============================================================
# HAVERSINE
# ============================================================
def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distance in km between two GPS points."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(
        math.radians(lat2)
    ) * math.sin(dlon / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Bearing in degrees from point 1 to point 2."""
    dlon = math.radians(lon2 - lon1)
    lat1r, lat2r = math.radians(lat1), math.radians(lat2)
    x = math.sin(dlon) * math.cos(lat2r)
    y = math.cos(lat1r) * math.sin(lat2r) - math.sin(lat1r) * math.cos(
        lat2r
    ) * math.cos(dlon)
    return (math.degrees(math.atan2(x, y)) + 360) % 360


# ============================================================
# COLOR HELPERS
# ============================================================
def _grade_color(gradient: float) -> str:
    """Color for gradient percentage (VeloViewer style)."""
    if gradient < -3:
        return "#2563eb"  # steep descent - blue
    if gradient < 0:
        return "#60a5fa"  # gentle descent - light blue
    if gradient < 3:
        return "#22c55e"  # flat - green
    if gradient < 6:
        return "#eab308"  # moderate - yellow
    if gradient < 9:
        return "#f97316"  # steep - orange
    if gradient < 12:
        return "#ef4444"  # very steep - red
    return "#7c2d12"  # extreme - dark red


def _wind_color(direction: str) -> str:
    """Color based on wind direction relative to rider."""
    if direction == "cara":
        return "#ef4444"  # headwind - red
    if direction == "costado":
        return "#f97316"  # crosswind - orange
    if direction == "cola":
        return "#22c55e"  # tailwind - green
    return "#6b7280"  # unknown - gray


def _rain_color(mm: float) -> str:
    """Color based on precipitation amount."""
    if mm < 0.1:
        return "#22c55e"  # dry - green
    if mm < 1.0:
        return "#60a5fa"  # light - blue
    if mm < 3.0:
        return "#3b82f6"  # moderate - blue
    return "#1d4ed8"  # heavy - dark blue


def _danger_color(danger_idx: float) -> str:
    """Color based on danger index (0-10)."""
    if danger_idx < 2:
        return "#22c55e"
    if danger_idx < 4:
        return "#eab308"
    if danger_idx < 6:
        return "#f97316"
    if danger_idx < 8:
        return "#ef4444"
    return "#7c2d12"


def _surface_color(surface: str) -> str:
    """Color based on surface type."""
    mapping = {
        "asphalt": "#6b7280",
        "gravel": "#d97706",
        "dirt": "#92400e",
        "cobblestone": "#78716c",
        "unpaved": "#b45309",
        "compacted": "#a3a3a3",
        "grass": "#16a34a",
        "sand": "#fbbf24",
        "concrete": "#9ca3af",
    }
    return mapping.get(surface, "#6b7280")


# ============================================================
# WIND DIRECTION RELATIVE TO RIDER
# ============================================================
def _relative_wind(rider_bearing: float, wind_direction: float) -> str:
    """Determine wind direction relative to rider."""
    # wind_direction is where wind comes FROM (meteorological)
    diff = abs(((wind_direction - rider_bearing) + 180) % 360 - 180)
    if diff < 45:
        return "cara"  # headwind
    if diff > 135:
        return "cola"  # tailwind
    return "costado"  # crosswind


# ============================================================
# GRADIENT COMPUTATION
# ============================================================
def _compute_gradients(dists: list[float], alts: list[float], window: int = 5) -> list[float]:
    """Compute smoothed gradient percentages."""
    n = len(dists)
    if n < 2:
        return [0.0] * n

    raw = []
    for i in range(n):
        if i == 0:
            raw.append(0.0)
        else:
            dx = (dists[i] - dists[i - 1]) * 1000  # km to m
            dy = alts[i] - alts[i - 1]
            raw.append((dy / dx * 100) if dx > 0 else 0.0)

    # Smooth with rolling average
    arr = np.array(raw)
    kernel = np.ones(window) / window
    smoothed = np.convolve(arr, kernel, mode="same")
    return [round(float(g), 2) for g in smoothed]


# ============================================================
# ENERGY COMPUTATION
# ============================================================
def _compute_energy(
    dists: list[float],
    alts: list[float],
    pends: list[float],
    weight: float,
    ftp_wkg: float,
) -> dict[str, Any]:
    """Compute energy expenditure and estimated time."""
    total_kj = 0.0
    total_time_s = 0.0
    d_pos = 0.0
    d_neg = 0.0
    ftp_w = ftp_wkg * weight

    for i in range(1, len(dists)):
        dx_km = dists[i] - dists[i - 1]
        if dx_km <= 0:
            continue
        dx_m = dx_km * 1000
        dy = alts[i] - alts[i - 1]

        if dy > 0:
            d_pos += dy
        else:
            d_neg += abs(dy)

        # Simplified power model
        grade = pends[i] / 100
        gravity_w = weight * 9.81 * grade  # climbing resistance
        rolling_w = weight * 9.81 * 0.005  # rolling resistance (Crr=0.005)
        aero_w = 0.5 * 1.2 * 0.35 * 0.5 * (10 ** 2)  # ~21W at 10m/s baseline

        total_power = max(gravity_w + rolling_w + aero_w, 50)
        # Assume rider can sustain ~75% FTP on average
        sustainable_w = ftp_w * 0.75
        speed_mps = max(sustainable_w / total_power * 10, 2)  # baseline 10 m/s

        segment_time = dx_m / speed_mps
        total_time_s += segment_time
        total_kj += sustainable_w * segment_time / 1000

    return {
        "d_pos": round(d_pos),
        "d_neg": round(d_neg),
        "total_kj": round(total_kj),
        "est_time_min": round(total_time_s / 60, 1),
    }


# ============================================================
# DANGER INDEX
# ============================================================
def _danger_index(
    gradient: float,
    wind_dir: str,
    rain_mm: float,
    surface: str,
) -> float:
    """Compute a 0-10 danger index based on multiple factors."""
    score = 0.0

    # Gradient contribution (steep descents are dangerous)
    if gradient < -6:
        score += 3.0
    elif gradient < -3:
        score += 1.5
    elif gradient > 9:
        score += 1.0

    # Wind
    if wind_dir == "costado":
        score += 2.5
    elif wind_dir == "cara":
        score += 1.0

    # Rain
    if rain_mm > 3:
        score += 3.0
    elif rain_mm > 1:
        score += 2.0
    elif rain_mm > 0.1:
        score += 1.0

    # Surface
    if surface in ("gravel", "dirt", "cobblestone", "sand"):
        score += 2.0
    elif surface in ("unpaved", "compacted"):
        score += 1.0

    return min(score, 10.0)


# ============================================================
# ROADBOOK BUILDER
# ============================================================
def _build_roadbook(
    dists: list[float],
    alts: list[float],
    pends: list[float],
    wind_dirs: list[str],
    rain_km: list[float],
    surf_map: list[str],
) -> list[dict[str, Any]]:
    """Build tactical roadbook events from analysis data."""
    events: list[dict[str, Any]] = []
    n = len(dists)
    if n < 5:
        return events

    # Detect climbs (sustained gradient > 4%)
    in_climb = False
    climb_start = 0
    for i in range(n):
        if pends[i] > 4 and not in_climb:
            in_climb = True
            climb_start = i
        elif (pends[i] < 2 or i == n - 1) and in_climb:
            in_climb = False
            km_start = round(dists[climb_start], 1)
            km_end = round(dists[i], 1)
            max_grad = max(pends[climb_start:i + 1])
            d_plus = sum(
                alts[j] - alts[j - 1]
                for j in range(climb_start + 1, i + 1)
                if alts[j] > alts[j - 1]
            )
            severity = "high" if max_grad > 8 else "medium"
            events.append({
                "type": "climb",
                "km": km_start,
                "km_end": km_end,
                "label": f"Puerto: {round(d_plus)}m D+ · max {round(max_grad, 1)}%",
                "severity": severity,
            })

    # Detect steep descents (sustained gradient < -5%)
    in_desc = False
    desc_start = 0
    for i in range(n):
        if pends[i] < -5 and not in_desc:
            in_desc = True
            desc_start = i
        elif (pends[i] > -3 or i == n - 1) and in_desc:
            in_desc = False
            km_start = round(dists[desc_start], 1)
            km_end = round(dists[i], 1)
            min_grad = min(pends[desc_start:i + 1])
            events.append({
                "type": "descent",
                "km": km_start,
                "km_end": km_end,
                "label": f"Descenso tecnico: max {round(abs(min_grad), 1)}%",
                "severity": "high" if min_grad < -8 else "medium",
            })

    # Detect crosswind zones (sustained crosswind > 3 consecutive points)
    wind_count = 0
    wind_start = 0
    for i in range(n):
        if wind_dirs[i] == "costado":
            if wind_count == 0:
                wind_start = i
            wind_count += 1
        else:
            if wind_count >= 3:
                events.append({
                    "type": "wind",
                    "km": round(dists[wind_start], 1),
                    "km_end": round(dists[i], 1),
                    "label": f"Zona de viento lateral · {round(dists[i] - dists[wind_start], 1)} km",
                    "severity": "high",
                })
            wind_count = 0

    # Detect rain zones
    rain_count = 0
    rain_start = 0
    for i in range(n):
        if rain_km[i] > 0.1:
            if rain_count == 0:
                rain_start = i
            rain_count += 1
        else:
            if rain_count >= 3:
                max_rain = max(rain_km[rain_start:i])
                events.append({
                    "type": "rain",
                    "km": round(dists[rain_start], 1),
                    "km_end": round(dists[i], 1),
                    "label": f"Lluvia: max {round(max_rain, 1)} mm/h",
                    "severity": "high" if max_rain > 3 else "medium",
                })
            rain_count = 0

    # Sort by km
    events.sort(key=lambda e: e["km"])
    return events


# ============================================================
# PLOTLY FIGURE BUILDER
# ============================================================
def _build_plotly_figure(
    dists: list[float],
    alts: list[float],
    colors: list[str],
) -> dict[str, Any]:
    """Build Plotly figure JSON for the elevation profile."""
    # Main bar trace (elevation profile)
    bar = go.Bar(
        x=dists,
        y=alts,
        marker=dict(color=colors, line=dict(width=0)),
        hovertemplate="Km %{x:.1f}<br>Alt %{y:.0f}m<extra></extra>",
        name="Perfil",
    )

    # Staff trace for waypoints (empty initially)
    staff = go.Scatter(
        x=[],
        y=[],
        mode="markers+text",
        marker=dict(size=10, color="#ff3e3e", symbol="diamond"),
        textposition="top center",
        textfont=dict(size=10, color="#ff3e3e"),
        text=[],
        name="Waypoints",
        hoverinfo="text",
    )

    # Cursor trace
    cursor = go.Scatter(
        x=[dists[0] if dists else 0],
        y=[alts[0] if alts else 0],
        mode="markers",
        marker=dict(size=12, color="#ffffff", symbol="circle", line=dict(width=2, color="#ff3e3e")),
        name="Cursor",
        hoverinfo="skip",
    )

    layout = go.Layout(
        paper_bgcolor="#0f1115",
        plot_bgcolor="#0f1115",
        margin=dict(l=50, r=20, t=20, b=40),
        xaxis=dict(
            title="Distancia (km)",
            color="#8a95a8",
            gridcolor="#252932",
            zeroline=False,
        ),
        yaxis=dict(
            title="Altitud (m)",
            color="#8a95a8",
            gridcolor="#252932",
            zeroline=False,
        ),
        font=dict(family="Outfit, sans-serif", color="#e8e8e8"),
        showlegend=False,
        dragmode="zoom",
        hovermode="x unified",
    )

    fig = go.Figure(data=[bar, staff, cursor], layout=layout)
    return fig.to_dict()


# ============================================================
# TACTICAL SUMMARY
# ============================================================
def _build_tactical_summary(
    stats: dict[str, Any],
    roadbook: list[dict[str, Any]],
) -> dict[str, str]:
    """Generate a one-paragraph tactical briefing."""
    climbs = [e for e in roadbook if e["type"] == "climb"]
    descents = [e for e in roadbook if e["type"] == "descent"]
    wind_zones = [e for e in roadbook if e["type"] == "wind"]
    rain_zones = [e for e in roadbook if e["type"] == "rain"]

    parts = []
    parts.append(f"Etapa de {stats.get('d_pos', 0)}m D+ con {len(climbs)} puerto(s).")

    if descents:
        parts.append(f"{len(descents)} descenso(s) tecnico(s).")
    if wind_zones:
        parts.append(f"Atencion: {len(wind_zones)} zona(s) de viento lateral.")
    if rain_zones:
        parts.append(f"Prevision de lluvia en {len(rain_zones)} tramo(s).")

    est_time = stats.get("est_time_min", 0)
    if est_time:
        hours = int(est_time // 60)
        mins = int(est_time % 60)
        parts.append(f"Tiempo estimado: {hours}h{mins:02d}.")

    high_events = [e for e in roadbook if e.get("severity") == "high"]
    if high_events:
        parts.append(f"{len(high_events)} evento(s) de prioridad ALTA.")

    return {"summary": " ".join(parts)}


# ============================================================
# MAIN ANALYSIS FUNCTION
# ============================================================
async def analyze_gpx(
    gpx_content: str,
    params: AnalysisParams,
    weather_data: dict[str, Any] | None = None,
    surface_data: list[str] | None = None,
    progress_callback: Any = None,
) -> AnalysisResult:
    """
    Main analysis pipeline. Parses GPX, computes all metrics.

    Args:
        gpx_content: Raw GPX XML string
        params: Analysis parameters (date, hour, weight, FTP)
        weather_data: Pre-fetched weather data (wind speed/dir, rain) or None
        surface_data: Pre-fetched surface types per point or None
        progress_callback: Async callable(msg, pct) for progress updates
    """
    result = AnalysisResult()

    async def emit(msg: str, pct: int):
        if progress_callback:
            await progress_callback(msg, pct)

    # Step 1: Parse GPX (with timeout protection)
    await emit("Parseando archivo GPX...", 10)
    try:
        gpx = await asyncio.wait_for(
            asyncio.get_event_loop().run_in_executor(None, gpxpy.parse, gpx_content),
            timeout=30.0,
        )
    except asyncio.TimeoutError:
        raise ValueError("GPX parsing timeout (>30s) — archivo posiblemente corrupto o malicioso")

    # Extract track points
    points = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                points.append(point)

    if len(points) < 10:
        raise ValueError(f"GPX < 10 puntos ({len(points)} encontrados)")

    await emit("Extrayendo coordenadas...", 20)

    # Step 2: Extract coordinates and compute distances
    result.lats = [p.latitude for p in points]
    result.lons = [p.longitude for p in points]
    result.alts = [p.elevation or 0.0 for p in points]

    # Compute cumulative distances
    cum_dist = 0.0
    result.dists = [0.0]
    for i in range(1, len(points)):
        d = _haversine(
            result.lats[i - 1], result.lons[i - 1],
            result.lats[i], result.lons[i],
        )
        cum_dist += d
        result.dists.append(round(cum_dist, 3))

    # Compute bearings
    result.bearings = [0.0]
    for i in range(1, len(points)):
        b = _bearing(result.lats[i - 1], result.lons[i - 1], result.lats[i], result.lons[i])
        result.bearings.append(round(b, 1))

    await emit("Calculando pendientes...", 35)

    # Step 3: Compute gradients
    result.pends = _compute_gradients(result.dists, result.alts)

    # Step 4: Apply weather data
    await emit("Procesando datos meteorologicos...", 50)
    n = len(result.dists)

    if weather_data:
        wind_speed = weather_data.get("wind_speed", 0)
        wind_dir = weather_data.get("wind_direction", 0)
        rain_values = weather_data.get("rain", [0.0] * n)
        if isinstance(rain_values, (int, float)):
            rain_values = [float(rain_values)] * n
        # Ensure correct length
        while len(rain_values) < n:
            rain_values.append(rain_values[-1] if rain_values else 0.0)

        result.rain_km = [round(r, 2) for r in rain_values[:n]]
        result.wind_dirs = [
            _relative_wind(result.bearings[i], wind_dir) for i in range(n)
        ]
        result.stats["wind"] = {"speed": wind_speed, "direction": wind_dir}
    else:
        result.rain_km = [0.0] * n
        result.wind_dirs = ["desconocido"] * n
        result.stats["wind"] = {"speed": 0, "direction": 0}

    # Step 5: Apply surface data
    await emit("Procesando datos de pavimento...", 60)
    if surface_data and len(surface_data) >= n:
        result.surf_map = surface_data[:n]
    else:
        result.surf_map = ["asphalt"] * n

    # Step 6: Compute colors for all visualization modes
    await emit("Generando capas de visualizacion...", 70)
    result.colors_grade = [_grade_color(g) for g in result.pends]
    result.colors_wind = [_wind_color(w) for w in result.wind_dirs]
    result.colors_rain = [_rain_color(r) for r in result.rain_km]
    result.colors_surf = [_surface_color(s) for s in result.surf_map]

    # Danger index colors
    danger_indices = [
        _danger_index(result.pends[i], result.wind_dirs[i], result.rain_km[i], result.surf_map[i])
        for i in range(n)
    ]
    result.colors_danger = [_danger_color(d) for d in danger_indices]

    # Step 7: Compute energy
    await emit("Calculando energia y tiempo estimado...", 80)
    energy = _compute_energy(
        result.dists, result.alts, result.pends,
        params.rider_weight_kg, params.ftp_wkg,
    )
    result.stats.update(energy)

    # Step 8: Build roadbook
    await emit("Construyendo roadbook tactico...", 85)
    result.roadbook = _build_roadbook(
        result.dists, result.alts, result.pends,
        result.wind_dirs, result.rain_km, result.surf_map,
    )
    result.tactical_summary = _build_tactical_summary(result.stats, result.roadbook)

    # Step 9: Build Plotly figure
    await emit("Generando grafico de perfil...", 90)
    fig_dict = _build_plotly_figure(result.dists, result.alts, result.colors_grade)
    result.fig_json = fig_dict
    result.idx_staff = 1  # index of staff trace in fig.data
    result.idx_cursor = 2  # index of cursor trace in fig.data

    await emit("Analisis completado", 100)
    return result
