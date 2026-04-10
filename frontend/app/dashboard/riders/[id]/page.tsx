"use client";

import { useEffect, useState, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import { api } from "@/lib/api";
import type { Rider, FTPHistoryEntry } from "@/types/database";

export default function RiderDetailPage() {
  const { id } = useParams();
  const router = useRouter();
  const [rider, setRider] = useState<(Rider & { ftp_history: FTPHistoryEntry[] }) | null>(null);
  const [notes, setNotes] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (id) loadRider(id as string);
  }, [id]);

  async function loadRider(riderId: string) {
    const data = await api.get<Rider & { ftp_history: FTPHistoryEntry[] }>(
      `/api/riders/${riderId}`
    );
    setRider(data);
    setNotes(data.notes || "");
  }

  // Auto-save notes on blur with debounce
  const saveNotes = useCallback(async () => {
    if (!rider) return;
    setSaving(true);
    await api.patch(`/api/riders/${rider.id}`, { notes });
    setSaving(false);
  }, [rider, notes]);

  async function handleArchive() {
    if (!rider || !confirm("Archivar ciclista?")) return;
    await api.delete(`/api/riders/${rider.id}`);
    router.push("/dashboard/riders");
  }

  if (!rider) {
    return <div className="flex h-full items-center justify-center text-muted">Cargando...</div>;
  }

  return (
    <div className="mx-auto max-w-4xl p-6">
      {/* Header */}
      <div className="mb-6 flex items-center gap-4">
        <div className="flex h-16 w-16 items-center justify-center rounded-full bg-panel-2 text-2xl font-bold text-accent">
          {rider.full_name.charAt(0)}
        </div>
        <div>
          <h1 className="text-2xl font-extrabold">{rider.full_name}</h1>
          <div className="text-sm text-muted">
            {rider.nationality || "—"} · {rider.status} · {rider.birth_date || "—"}
          </div>
        </div>
        <button
          onClick={handleArchive}
          className="ml-auto rounded-lg border border-line px-4 py-2 text-xs font-semibold text-muted transition hover:border-accent hover:text-accent"
        >
          Archivar
        </button>
      </div>

      {/* Stats grid */}
      <div className="mb-6 grid grid-cols-2 gap-4 sm:grid-cols-4">
        <StatCard label="Peso" value={`${rider.weight_kg ?? "—"} kg`} />
        <StatCard label="Altura" value={`${rider.height_cm ?? "—"} cm`} />
        <StatCard label="FTP" value={`${rider.ftp_w ?? "—"} W`} />
        <StatCard label="W/kg" value={`${rider.ftp_wkg ?? "—"}`} />
        <StatCard label="VO2max" value={`${rider.vo2max ?? "—"}`} />
        <StatCard label="Contrato" value={rider.contract_end || "—"} />
      </div>

      {/* FTP History */}
      {rider.ftp_history && rider.ftp_history.length > 0 && (
        <div className="mb-6 rounded-xl border border-line bg-panel p-4">
          <h2 className="mb-3 text-sm font-bold uppercase tracking-wider text-muted">
            Historial FTP
          </h2>
          <div className="space-y-1">
            {rider.ftp_history.map((entry) => (
              <div
                key={entry.id}
                className="flex justify-between border-b border-line py-1.5 text-sm"
              >
                <span className="text-muted">{entry.date}</span>
                <span className="font-mono font-semibold">
                  {entry.ftp_w}W · {entry.ftp_wkg ?? "—"} W/kg
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Notes */}
      <div className="rounded-xl border border-line bg-panel p-4">
        <h2 className="mb-3 text-sm font-bold uppercase tracking-wider text-muted">
          Notas {saving && <span className="text-xs text-accent">guardando...</span>}
        </h2>
        <textarea
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          onBlur={saveNotes}
          rows={4}
          className="w-full rounded-lg border border-line bg-background p-3 text-sm text-white outline-none focus:border-accent"
          placeholder="Notas sobre el ciclista..."
        />
      </div>
    </div>
  );
}

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-line bg-panel-2 p-3 text-center">
      <div className="text-[11px] uppercase tracking-wider text-muted">{label}</div>
      <div className="mt-1 font-mono text-lg font-semibold">{value}</div>
    </div>
  );
}
