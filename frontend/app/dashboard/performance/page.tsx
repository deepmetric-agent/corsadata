"use client";

import { useEffect, useRef, useState } from "react";
import { api } from "@/lib/api";
import type { PerformanceEntry, Rider } from "@/types/database";

export default function PerformancePage() {
  const [riders, setRiders] = useState<Rider[]>([]);
  const [selected, setSelected] = useState<string[]>([]);
  const [entries, setEntries] = useState<PerformanceEntry[]>([]);
  const fileRef = useRef<HTMLInputElement>(null);
  const [importResult, setImportResult] = useState<{ imported: number; errors: any[] } | null>(null);

  useEffect(() => {
    api.get<Rider[]>("/api/riders?status=active").then(setRiders).catch(() => {});
  }, []);

  useEffect(() => {
    if (selected.length === 0) {
      setEntries([]);
      return;
    }
    // Fetch performance for all selected riders
    Promise.all(
      selected.map((id) => api.get<PerformanceEntry[]>(`/api/performance?rider_id=${id}`))
    ).then((results) => {
      setEntries(results.flat());
    });
  }, [selected]);

  function toggleRider(id: string) {
    setSelected((s) =>
      s.includes(id) ? s.filter((x) => x !== id) : s.length < 4 ? [...s, id] : s
    );
  }

  async function handleImport() {
    const file = fileRef.current?.files?.[0];
    if (!file) return;
    const fd = new FormData();
    fd.append("file", file);
    const result = await api.post<{ imported: number; errors: any[] }>("/api/performance/import", fd);
    setImportResult(result);
  }

  return (
    <div className="p-6">
      <h1 className="mb-6 text-2xl font-extrabold">Rendimiento</h1>

      {/* Rider selector */}
      <div className="mb-4">
        <div className="mb-2 text-xs font-semibold uppercase tracking-wider text-muted">
          Seleccionar ciclistas (max 4)
        </div>
        <div className="flex flex-wrap gap-2">
          {riders.map((r) => (
            <button
              key={r.id}
              onClick={() => toggleRider(r.id)}
              className={`rounded-lg border px-3 py-1.5 text-xs font-semibold transition ${
                selected.includes(r.id)
                  ? "border-accent bg-accent/20 text-accent"
                  : "border-line text-muted hover:border-accent"
              }`}
            >
              {r.full_name}
            </button>
          ))}
        </div>
      </div>

      {/* Performance table */}
      {entries.length > 0 && (
        <div className="mb-6 overflow-x-auto rounded-xl border border-line">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-panel-2 text-xs uppercase tracking-wider text-muted">
                <th className="px-4 py-2.5 text-left">Fecha</th>
                <th className="px-4 py-2.5 text-left">Tipo</th>
                <th className="px-4 py-2.5 text-right">Dist (km)</th>
                <th className="px-4 py-2.5 text-right">Duracion (min)</th>
                <th className="px-4 py-2.5 text-right">Pot media (W)</th>
                <th className="px-4 py-2.5 text-right">NP (W)</th>
                <th className="px-4 py-2.5 text-right">TSS</th>
              </tr>
            </thead>
            <tbody>
              {entries.slice(0, 50).map((e) => (
                <tr key={e.id} className="border-t border-line hover:bg-panel-2/50">
                  <td className="px-4 py-2 font-mono">{e.date}</td>
                  <td className="px-4 py-2">{e.type || "—"}</td>
                  <td className="px-4 py-2 text-right font-mono">{e.distance_km ?? "—"}</td>
                  <td className="px-4 py-2 text-right font-mono">{e.duration_min ?? "—"}</td>
                  <td className="px-4 py-2 text-right font-mono">{e.avg_power_w ?? "—"}</td>
                  <td className="px-4 py-2 text-right font-mono">{e.normalized_power_w ?? "—"}</td>
                  <td className="px-4 py-2 text-right font-mono">{e.tss ?? "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* CSV Import */}
      <div className="rounded-xl border border-line bg-panel p-4">
        <h2 className="mb-3 text-sm font-bold uppercase tracking-wider text-muted">
          Importar CSV
        </h2>
        <div className="flex items-center gap-3">
          <input ref={fileRef} type="file" accept=".csv" className="text-sm text-muted" />
          <button
            onClick={handleImport}
            className="rounded-lg bg-accent px-4 py-2 text-xs font-bold text-white transition hover:bg-accent-hover"
          >
            Importar
          </button>
        </div>
        {importResult && (
          <div className="mt-3 text-xs">
            <span className="text-green-ok">{importResult.imported} importados</span>
            {importResult.errors.length > 0 && (
              <span className="ml-2 text-accent">
                {importResult.errors.length} errores
              </span>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
