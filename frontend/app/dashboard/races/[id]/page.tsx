"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { api } from "@/lib/api";
import type { Race, RaceEntry, Stage } from "@/types/database";

interface RaceDetail extends Race {
  entries: (RaceEntry & { riders?: { full_name: string; nationality: string; status: string } })[];
  stages: Stage[];
}

export default function RaceDetailPage() {
  const { id } = useParams();
  const [race, setRace] = useState<RaceDetail | null>(null);

  useEffect(() => {
    if (id) api.get<RaceDetail>(`/api/races/${id}`).then(setRace).catch(() => {});
  }, [id]);

  if (!race) {
    return <div className="flex h-full items-center justify-center text-muted">Cargando...</div>;
  }

  return (
    <div className="mx-auto max-w-4xl p-6">
      <h1 className="mb-2 text-2xl font-extrabold">{race.name}</h1>
      <div className="mb-6 text-sm text-muted">
        {race.start_date} → {race.end_date} · {race.country || "—"} · {race.category || "—"} · {race.status}
      </div>

      {/* Convocados */}
      <section className="mb-6">
        <h2 className="mb-3 text-sm font-bold uppercase tracking-wider text-muted">
          Ciclistas convocados ({race.entries.length})
        </h2>
        {race.entries.length === 0 ? (
          <p className="text-xs text-muted">Sin ciclistas asignados</p>
        ) : (
          <div className="space-y-1.5">
            {race.entries.map((entry) => (
              <div
                key={entry.id}
                className="flex items-center justify-between rounded-lg border border-line bg-panel-2 px-4 py-2.5"
              >
                <div>
                  <span className="font-semibold">{entry.riders?.full_name || "—"}</span>
                  <span className="ml-2 text-xs text-muted">{entry.role || "Sin rol"}</span>
                </div>
                {entry.result && (
                  <span className="font-mono text-xs font-semibold text-accent">{entry.result}</span>
                )}
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Etapas vinculadas */}
      <section>
        <h2 className="mb-3 text-sm font-bold uppercase tracking-wider text-muted">
          Etapas analizadas ({race.stages.length})
        </h2>
        {race.stages.length === 0 ? (
          <p className="text-xs text-muted">Sin etapas vinculadas</p>
        ) : (
          <div className="space-y-1.5">
            {race.stages.map((stage) => (
              <div
                key={stage.id}
                className="rounded-lg border border-line bg-panel-2 px-4 py-2.5"
              >
                <div className="font-semibold">{stage.name}</div>
                <div className="text-xs text-muted">
                  {stage.distance_km ?? "?"}km · D+{stage.d_pos_m ?? "?"}m
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
