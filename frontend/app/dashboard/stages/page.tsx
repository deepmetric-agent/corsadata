"use client";

import { useState } from "react";
import { ProfileChart } from "@/components/analysis/ProfileChart";
import { StageLibrary } from "@/components/analysis/StageLibrary";
import { RoadbookPanel } from "@/components/analysis/RoadbookPanel";
import { MapView } from "@/components/analysis/MapView";
import { AnalysisParams } from "@/components/analysis/AnalysisParams";
import { StatsPanel } from "@/components/analysis/StatsPanel";
import { WaypointPanel, WaypointList } from "@/components/analysis/WaypointPanel";
import { ProgressOverlay } from "@/components/analysis/ProgressOverlay";
import { useAnalysisStore } from "@/lib/stores/analysis-store";

export default function StagesPage() {
  const { data } = useAnalysisStore();
  const [hoverKm, setHoverKm] = useState<number | null>(null);
  const [pendingWp, setPendingWp] = useState<{ km: number; alt: number } | null>(null);

  function handleChartHover(km: number) {
    setHoverKm(km);
  }

  function handleChartClick(km: number, alt: number) {
    setPendingWp({ km, alt });
  }

  function handleJumpTo(km: number) {
    setHoverKm(km);
  }

  return (
    <div className="flex h-full overflow-hidden">
      {/* LEFT SIDEBAR (300px) */}
      <aside className="flex w-[300px] flex-shrink-0 flex-col overflow-y-auto border-r border-line bg-panel p-3.5">
        <SectionTitle>MIS ETAPAS</SectionTitle>
        <StageLibrary />

        <SectionTitle className="mt-4">PARAMETROS</SectionTitle>
        <AnalysisParams />

        {data && (
          <>
            <SectionTitle className="mt-4">ESTADISTICAS</SectionTitle>
            <StatsPanel />

            <SectionTitle className="mt-4">WAYPOINTS</SectionTitle>
            <WaypointList />
          </>
        )}
      </aside>

      {/* MAIN CONTENT */}
      <div className="flex min-w-0 flex-1 flex-col">
        {/* Profile Chart (55% height) */}
        <div className="relative min-h-[300px]" style={{ height: "55%" }}>
          <ProfileChart onHover={handleChartHover} onClick={handleChartClick} />
        </div>

        {/* Map (45% height) */}
        {data?.lats && (
          <div style={{ height: "45%" }}>
            <MapView hoverKm={hoverKm} />
          </div>
        )}
      </div>

      {/* RIGHT PANEL — ROADBOOK (320px) */}
      <aside className="w-[320px] flex-shrink-0 border-l border-line bg-panel">
        <RoadbookPanel onJumpTo={handleJumpTo} />
      </aside>

      {/* Waypoint creation panel */}
      {pendingWp && (
        <WaypointPanel
          pendingKm={pendingWp.km}
          pendingAlt={pendingWp.alt}
          onClose={() => setPendingWp(null)}
        />
      )}

      {/* Loading overlay */}
      <ProgressOverlay />
    </div>
  );
}

function SectionTitle({
  children,
  className = "",
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div
      className={`mb-2 text-[11px] font-bold uppercase tracking-[2px] text-muted ${className}`}
    >
      {children}
    </div>
  );
}
