"use client";

import { useAnalysisStore } from "@/lib/stores/analysis-store";

interface RoadbookPanelProps {
  onJumpTo?: (km: number) => void;
}

const ICONS: Record<string, string> = {
  climb: "⛰",
  wind: "💨",
  descent: "⚠️",
  rain: "🌧",
};

export function RoadbookPanel({ onJumpTo }: RoadbookPanelProps) {
  const { data } = useAnalysisStore();
  const roadbook = data?.roadbook || [];
  const summary = data?.tactical_summary?.summary || "Analiza una etapa para ver el briefing tactico.";

  return (
    <div className="flex h-full flex-col">
      <div className="border-b border-line bg-panel-2 px-4 py-3.5 text-xs font-extrabold uppercase tracking-[2px] text-accent">
        ROADBOOK TACTICO
      </div>

      <div className="border-b border-line px-4 py-2.5 text-xs leading-relaxed text-muted">
        {summary}
      </div>

      <div className="flex-1 overflow-y-auto p-2.5">
        {roadbook.length === 0 ? (
          <div className="mt-10 text-center text-sm opacity-30">Sin eventos</div>
        ) : (
          roadbook.map((event, i) => (
            <button
              key={i}
              onClick={() => onJumpTo?.(event.km)}
              className={`mb-2 w-full rounded-lg bg-panel-2 p-3 text-left transition hover:translate-x-0.5 hover:bg-[#2d3440] ${
                event.severity === "high"
                  ? "border-l-4 border-accent"
                  : event.severity === "medium"
                  ? "border-l-4 border-[#ffb020]"
                  : "border-l-4 border-line"
              }`}
            >
              <div className="font-mono text-[15px] font-bold text-accent">
                {ICONS[event.type] || "📍"} KM {event.km}
                {event.km_end ? ` → ${event.km_end}` : ""}
              </div>
              <div className="mt-1 text-[13px] font-semibold">{event.label}</div>
              <div className="mt-0.5 text-[11px] text-muted">
                {event.type}
                {event.severity === "high" ? " · PRIORIDAD ALTA" : ""}
              </div>
            </button>
          ))
        )}
      </div>
    </div>
  );
}
