"use client";

import { useAnalysisStore } from "@/lib/stores/analysis-store";
import { api } from "@/lib/api";

interface WaypointPanelProps {
  pendingKm: number | null;
  pendingAlt: number | null;
  onClose: () => void;
}

const WP_TYPES = [
  { label: "🚰 Avituallamiento", type: "avit" },
  { label: "⚠️ Peligro", type: "danger" },
  { label: "🏁 Sprint", type: "sprint" },
  { label: "📍 Punto clave", type: "key" },
];

export function WaypointPanel({ pendingKm, pendingAlt, onClose }: WaypointPanelProps) {
  const { data, addWaypoint, wpList, removeWaypoint } = useAnalysisStore();

  if (pendingKm === null || !data) return null;

  // Find lat/lon for the km
  const dists = data.dists;
  let idx = 0;
  for (let i = 1; i < dists.length; i++) {
    if (Math.abs(dists[i] - pendingKm) < Math.abs(dists[idx] - pendingKm)) idx = i;
  }
  const r = data.lats.length / dists.length;
  const mi = Math.min(Math.floor(idx * r), data.lats.length - 1);
  const lat = data.lats[mi];
  const lon = data.lons[mi];

  function handleAdd(label: string, type: string) {
    addWaypoint({
      id: `wp-${Date.now()}`,
      analysis_id: "",
      team_id: "",
      name: label,
      type,
      km: pendingKm!,
      lat,
      lon,
      alt: pendingAlt,
      created_at: "",
    });
    onClose();
  }

  return (
    <div className="fixed left-[320px] top-1/2 z-[100] w-[240px] -translate-y-1/2 rounded-xl border border-line bg-panel p-4 shadow-2xl">
      <h4 className="mb-3 text-xs font-bold uppercase tracking-[2px] text-muted">
        Anadir Waypoint
      </h4>
      {WP_TYPES.map((wp) => (
        <button
          key={wp.type}
          onClick={() => handleAdd(wp.label, wp.type)}
          className="mb-1.5 flex w-full items-center gap-2 rounded-lg border border-line bg-panel-2 px-3 py-2.5 text-xs font-medium transition hover:border-accent hover:text-accent"
        >
          {wp.label}
        </button>
      ))}
      <button
        onClick={onClose}
        className="mt-1 w-full rounded-lg border border-line bg-panel-2 px-3 py-2.5 text-xs text-muted transition hover:border-accent"
      >
        Cancelar
      </button>
    </div>
  );
}

export function WaypointList() {
  const { wpList, removeWaypoint } = useAnalysisStore();

  if (!wpList.length) {
    return <span className="text-[11px] text-muted">Sin waypoints</span>;
  }

  return (
    <div className="space-y-0">
      {wpList.map((wp, i) => (
        <div
          key={i}
          className="flex items-center justify-between border-b border-line py-1 text-[11px]"
        >
          <span>
            {wp.name} · km {wp.km?.toFixed(1)}
          </span>
          <button
            onClick={() => removeWaypoint(i)}
            className="cursor-pointer text-accent"
          >
            ✕
          </button>
        </div>
      ))}
    </div>
  );
}
