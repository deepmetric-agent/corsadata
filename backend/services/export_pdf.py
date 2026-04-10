"""
PDF Export — Generate analysis report with roadbook and stats.
Uses ReportLab for PDF generation.
"""
from __future__ import annotations

import io
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def generate_pdf_report(
    stage_name: str,
    stage_data: dict[str, Any],
    stats: dict[str, Any],
    roadbook: list[dict[str, Any]],
    waypoints: list[dict[str, Any]],
) -> bytes:
    """Generate a PDF report and return bytes."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=20 * mm, bottomMargin=20 * mm)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Title"],
        fontSize=20,
        spaceAfter=6 * mm,
        textColor=colors.HexColor("#ff3e3e"),
    )
    elements.append(Paragraph(f"Director Hub PRO — {stage_name}", title_style))

    # Stats section
    elements.append(Paragraph("Estadisticas de la Etapa", styles["Heading2"]))

    stats_data = [
        ["Metrica", "Valor"],
        ["Distancia", f"{stage_data.get('distance_km', '?')} km"],
        ["Desnivel +", f"{stats.get('d_pos', '?')} m"],
        ["Desnivel -", f"{stats.get('d_neg', '?')} m"],
        ["Energia total", f"{stats.get('total_kj', '?')} kJ"],
    ]

    est_time = stats.get("est_time_min", 0)
    if est_time:
        hours = int(est_time // 60)
        mins = int(est_time % 60)
        stats_data.append(["Tiempo estimado", f"{hours}h{mins:02d}"])

    wind = stats.get("wind", {})
    if wind.get("speed"):
        stats_data.append(["Viento", f"{wind['speed']} km/h — {wind.get('direction', 0)}°"])

    stats_table = Table(stats_data, colWidths=[60 * mm, 80 * mm])
    stats_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1d23")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#343844")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f5f5f5"), colors.white]),
    ]))
    elements.append(stats_table)
    elements.append(Spacer(1, 8 * mm))

    # Roadbook section
    if roadbook:
        elements.append(Paragraph("Roadbook Tactico", styles["Heading2"]))

        rb_data = [["Km", "Tipo", "Descripcion", "Prioridad"]]
        for event in sorted(roadbook, key=lambda e: e.get("km", 0)):
            km_str = str(event.get("km", ""))
            if event.get("km_end"):
                km_str += f" → {event['km_end']}"
            rb_data.append([
                km_str,
                event.get("type", ""),
                event.get("label", ""),
                event.get("severity", "").upper(),
            ])

        rb_table = Table(rb_data, colWidths=[25 * mm, 25 * mm, 80 * mm, 25 * mm])
        rb_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1d23")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#343844")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f5f5f5"), colors.white]),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        elements.append(rb_table)
        elements.append(Spacer(1, 8 * mm))

    # Waypoints section
    if waypoints:
        elements.append(Paragraph("Waypoints", styles["Heading2"]))

        wp_data = [["Km", "Nombre", "Lat", "Lon"]]
        for wp in sorted(waypoints, key=lambda w: w.get("km", 0)):
            wp_data.append([
                f"{wp.get('km', 0):.1f}",
                wp.get("name", ""),
                f"{wp.get('lat', 0):.5f}",
                f"{wp.get('lon', 0):.5f}",
            ])

        wp_table = Table(wp_data, colWidths=[25 * mm, 60 * mm, 35 * mm, 35 * mm])
        wp_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1d23")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#343844")),
        ]))
        elements.append(wp_table)

    # Footer
    elements.append(Spacer(1, 10 * mm))
    footer_style = ParagraphStyle(
        "Footer", parent=styles["Normal"], fontSize=8, textColor=colors.gray,
    )
    elements.append(Paragraph("Generado por Director Hub PRO — Confidencial", footer_style))

    doc.build(elements)
    return buffer.getvalue()
