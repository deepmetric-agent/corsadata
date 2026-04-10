"use client";

import { useCallback, useEffect, useRef } from "react";
import { useAnalysisStore } from "@/lib/stores/analysis-store";

// Dynamic import of Plotly to avoid SSR issues
let Plotly: any = null;
if (typeof window !== "undefined") {
  Plotly = require("plotly.js-dist-min");
}

const TABS = [
  { key: "principal", label: "PRINCIPAL", icon: "" },
  { key: "rampas", label: "RAMPAS", icon: "" },
  { key: "viento", label: "VIENTO", icon: "" },
  { key: "lluvia", label: "LLUVIA", icon: "" },
  { key: "energia", label: "ENERGIA", icon: "" },
  { key: "pav", label: "PAVIMENTO", icon: "" },
] as const;

interface ProfileChartProps {
  onHover?: (km: number) => void;
  onClick?: (km: number, alt: number) => void;
}

export function ProfileChart({ onHover, onClick }: ProfileChartProps) {
  const chartRef = useRef<HTMLDivElement>(null);
  const plotRef = useRef<any>(null);
  const { data, figJson, activeTab, setActiveTab } = useAnalysisStore();

  // Render chart when figJson changes
  useEffect(() => {
    if (!figJson || !chartRef.current || !Plotly) return;

    const fig = typeof figJson === "string" ? JSON.parse(figJson) : figJson;

    Plotly.newPlot(chartRef.current, fig.data, fig.layout, {
      displaylogo: false,
      scrollZoom: true,
      responsive: true,
      modeBarButtonsToRemove: ["lasso2d", "autoScale2d"],
    }).then((gd: any) => {
      plotRef.current = gd;

      gd.on("plotly_hover", (ev: any) => {
        const p = ev.points?.find(
          (pt: any) => pt.data?.type !== "scattermapbox" && typeof pt.x === "number"
        );
        if (p && onHover) onHover(p.x);
      });

      gd.on("plotly_click", (ev: any) => {
        const p = ev.points?.find(
          (pt: any) => pt.data?.type !== "scattermapbox" && typeof pt.x === "number"
        );
        if (p && onClick) onClick(p.x, p.y);
      });
    });

    return () => {
      if (chartRef.current) Plotly.purge(chartRef.current);
    };
  }, [figJson]);

  // Recolor bars when tab changes
  const recolorBars = useCallback(
    (tab: string) => {
      if (!plotRef.current || !data) return;

      const colorMap: Record<string, string[] | undefined> = {
        principal: data.colors_grade,
        rampas: data.colors_grade,
        viento: data.colors_wind,
        lluvia: data.colors_rain,
        energia: data.colors_danger,
        pav: data.colors_surf,
      };

      const colors = colorMap[tab] || data.colors_grade;
      if (colors) {
        try {
          Plotly.restyle(plotRef.current, { "marker.color": [colors] }, [0]);
        } catch {}
      }
    },
    [data]
  );

  useEffect(() => {
    recolorBars(activeTab);
  }, [activeTab, recolorBars]);

  if (!figJson) {
    return (
      <div className="flex h-full flex-col items-center justify-center gap-3 text-center">
        <div className="text-5xl">🏔</div>
        <h2 className="text-xl font-extrabold">Sin etapa cargada</h2>
        <p className="max-w-[380px] text-sm text-muted">
          Selecciona una etapa de la libreria o carga un archivo GPX para iniciar
          el analisis tactico.
        </p>
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col">
      {/* Tabs */}
      <div className="flex gap-1 border-b border-line bg-panel px-4 py-2">
        {TABS.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key as any)}
            className={`rounded-lg px-4 py-1.5 text-xs font-semibold uppercase tracking-wider transition ${
              activeTab === tab.key
                ? "bg-accent text-white"
                : "text-muted hover:bg-panel-2 hover:text-white"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Chart */}
      <div ref={chartRef} className="flex-1" />
    </div>
  );
}
