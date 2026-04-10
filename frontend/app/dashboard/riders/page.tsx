"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import type { Rider } from "@/types/database";

export default function RidersPage() {
  const [riders, setRiders] = useState<Rider[]>([]);
  const [filter, setFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");

  useEffect(() => {
    loadRiders();
  }, [statusFilter]);

  async function loadRiders() {
    const params = new URLSearchParams();
    if (statusFilter) params.append("status", statusFilter);
    const data = await api.get<Rider[]>(`/api/riders?${params}`);
    setRiders(data);
  }

  const filtered = riders.filter((r) =>
    r.full_name.toLowerCase().includes(filter.toLowerCase())
  );

  return (
    <div className="p-6">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-extrabold">Ciclistas</h1>
        <Link
          href="/dashboard/riders/new"
          className="rounded-lg bg-accent px-4 py-2 text-sm font-bold text-white transition hover:bg-accent-hover"
        >
          + Nuevo ciclista
        </Link>
      </div>

      {/* Filters */}
      <div className="mb-4 flex gap-3">
        <input
          type="text"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          placeholder="Buscar por nombre..."
          className="rounded-lg border border-line bg-background px-4 py-2 text-sm text-white outline-none focus:border-accent"
        />
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="rounded-lg border border-line bg-background px-4 py-2 text-sm text-white"
        >
          <option value="">Todos</option>
          <option value="active">Activos</option>
          <option value="injured">Lesionados</option>
          <option value="inactive">Inactivos</option>
        </select>
      </div>

      {/* Grid */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {filtered.map((rider) => (
          <Link
            key={rider.id}
            href={`/dashboard/riders/${rider.id}`}
            className="rounded-xl border border-line bg-panel p-4 transition hover:border-accent"
          >
            <div className="flex items-center gap-3">
              <div className="flex h-12 w-12 items-center justify-center rounded-full bg-panel-2 text-lg font-bold text-accent">
                {rider.full_name.charAt(0)}
              </div>
              <div>
                <div className="font-bold">{rider.full_name}</div>
                <div className="text-xs text-muted">
                  {rider.nationality || "—"} ·{" "}
                  <span
                    className={
                      rider.status === "active"
                        ? "text-green-ok"
                        : rider.status === "injured"
                        ? "text-accent"
                        : "text-muted"
                    }
                  >
                    {rider.status}
                  </span>
                </div>
              </div>
            </div>
            <div className="mt-3 grid grid-cols-3 gap-2 text-center text-xs">
              <div>
                <div className="text-muted">Peso</div>
                <div className="font-mono font-semibold">{rider.weight_kg ?? "—"}</div>
              </div>
              <div>
                <div className="text-muted">FTP</div>
                <div className="font-mono font-semibold">{rider.ftp_w ?? "—"}W</div>
              </div>
              <div>
                <div className="text-muted">W/kg</div>
                <div className="font-mono font-semibold">{rider.ftp_wkg ?? "—"}</div>
              </div>
            </div>
            {rider.contract_end && isContractExpiring(rider.contract_end) && (
              <div className="mt-2 rounded bg-accent/20 px-2 py-1 text-center text-[10px] font-semibold text-accent">
                Contrato expira pronto
              </div>
            )}
          </Link>
        ))}
      </div>

      {filtered.length === 0 && (
        <div className="py-20 text-center text-muted">
          No se encontraron ciclistas
        </div>
      )}
    </div>
  );
}

function isContractExpiring(dateStr: string): boolean {
  const end = new Date(dateStr);
  const now = new Date();
  const diffDays = (end.getTime() - now.getTime()) / (1000 * 60 * 60 * 24);
  return diffDays > 0 && diffDays < 90;
}
