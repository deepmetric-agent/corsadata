"use client";

import { useAnalysisStore } from "@/lib/stores/analysis-store";

export function StatsPanel() {
  const { data } = useAnalysisStore();

  if (!data) return null;

  const stats = data.stats || {};
  const pends = data.pends || [];
  const r6 = pends.filter((p) => p >= 6).length;
  const maxGrad = pends.length ? Math.max(...pends) : 0;
  const wind = stats.wind || {};

  const windZones = (data.wind_dirs || []).filter((w) => w === "costado").length;
  const rainMax = data.rain_km?.length ? Math.max(...data.rain_km) : 0;
  const rainKm = (data.rain_km || []).filter((r) => r > 0.1).length;

  const estTime = stats.est_time_min || 0;
  const hours = Math.floor(estTime / 60);
  const mins = Math.round(estTime % 60);

  // Surface breakdown
  const surfs: Record<string, number> = {};
  (data.surf_map || []).forEach((s) => {
    surfs[s] = (surfs[s] || 0) + 1;
  });
  const SURF_LABELS: Record<string, string> = {
    asphalt: "Asfalto", gravel: "Gravilla", dirt: "Tierra",
    cobblestone: "Adoquin", unpaved: "Sin asfaltar", compacted: "Compactado",
    grass: "Hierba", sand: "Arena", concrete: "Hormigon",
  };

  return (
    <div className="space-y-3">
      <Section title="RAMPAS">
        <Stat label="Tramos >6%" value={`${r6} pts`} />
        <Stat label="Pendiente max" value={`${maxGrad.toFixed(1)}%`} />
        <Stat label="D+ total" value={`${stats.d_pos ?? "—"} m`} />
      </Section>

      <Section title="VIENTO">
        <Stat label="Velocidad" value={`${wind.speed?.toFixed(0) ?? "—"} km/h`} />
        <Stat label="Direccion" value={`${wind.direction?.toFixed(0) ?? "—"}°`} />
        <Stat label="Zonas costado" value={`${windZones} pts`} />
      </Section>

      <Section title="LLUVIA">
        <Stat label="Precipitacion" value={`${rainMax.toFixed(1)} mm`} />
        <Stat label="Km con lluvia" value={`${rainKm} pts`} />
      </Section>

      <Section title="ENERGIA">
        <Stat label="Energia total" value={`${stats.total_kj ?? "—"} kJ`} />
        <Stat label="Tiempo est." value={`${hours}h${String(mins).padStart(2, "0")}`} />
      </Section>

      <Section title="PAVIMENTO">
        {Object.entries(surfs)
          .filter(([k]) => k !== "asphalt")
          .map(([k, v]) => (
            <Stat key={k} label={SURF_LABELS[k] || k} value={`${v} pts`} />
          ))}
        {Object.keys(surfs).filter((k) => k !== "asphalt").length === 0 && (
          <Stat label="Solo asfalto" value="" />
        )}
      </Section>
    </div>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div>
      <div className="mb-1.5 text-[11px] font-bold uppercase tracking-[2px] text-muted">
        {title}
      </div>
      <div className="space-y-0">{children}</div>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between border-b border-line py-1 text-xs">
      <span className="text-muted">{label}</span>
      <span className="font-mono font-semibold">{value}</span>
    </div>
  );
}
