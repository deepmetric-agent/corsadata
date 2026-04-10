"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";

interface KPIs {
  riders: { total: number; active: number; injured: number; inactive: number };
  upcoming_races: number;
  recent_analyses: number;
  total_stages: number;
}

interface Alert {
  type: string;
  rider_id: string;
  rider_name: string;
  message: string;
}

export default function DashboardPage() {
  const [kpis, setKpis] = useState<KPIs | null>(null);
  const [alerts, setAlerts] = useState<Alert[]>([]);

  useEffect(() => {
    api.get<KPIs>("/api/dashboard/kpis").then(setKpis).catch(() => {});
    api.get<Alert[]>("/api/dashboard/alerts").then(setAlerts).catch(() => {});
  }, []);

  return (
    <div className="p-6">
      <h1 className="mb-6 text-2xl font-extrabold">Dashboard</h1>

      {/* KPI Cards */}
      <div className="mb-8 grid grid-cols-2 gap-4 lg:grid-cols-4">
        <KPICard
          label="Ciclistas activos"
          value={kpis?.riders.active ?? "—"}
          sub={`${kpis?.riders.injured ?? 0} lesionados`}
          href="/dashboard/riders"
        />
        <KPICard
          label="Proximas carreras"
          value={kpis?.upcoming_races ?? "—"}
          href="/dashboard/races"
        />
        <KPICard
          label="Analisis recientes"
          value={kpis?.recent_analyses ?? "—"}
          sub="Ultimos 30 dias"
          href="/dashboard/stages"
        />
        <KPICard
          label="Etapas totales"
          value={kpis?.total_stages ?? "—"}
          href="/dashboard/stages"
        />
      </div>

      {/* Alerts */}
      {alerts.length > 0 && (
        <div className="rounded-xl border border-line bg-panel p-4">
          <h2 className="mb-3 text-sm font-bold uppercase tracking-wider text-accent">
            Alertas ({alerts.length})
          </h2>
          <div className="space-y-2">
            {alerts.map((alert, i) => (
              <Link
                key={i}
                href={`/dashboard/riders/${alert.rider_id}`}
                className="flex items-center gap-3 rounded-lg border border-line bg-panel-2 px-4 py-2.5 text-sm transition hover:border-accent"
              >
                <span className="text-lg">
                  {alert.type === "ftp_outdated" ? "⚡" : "📋"}
                </span>
                <span>{alert.message}</span>
              </Link>
            ))}
          </div>
        </div>
      )}

      {/* Empty state if no KPIs loaded */}
      {!kpis && (
        <div className="py-20 text-center text-muted">Cargando datos del equipo...</div>
      )}
    </div>
  );
}

function KPICard({
  label,
  value,
  sub,
  href,
}: {
  label: string;
  value: number | string;
  sub?: string;
  href: string;
}) {
  return (
    <Link
      href={href}
      className="rounded-xl border border-line bg-panel p-5 transition hover:border-accent"
    >
      <div className="text-xs font-semibold uppercase tracking-wider text-muted">{label}</div>
      <div className="mt-2 font-mono text-3xl font-extrabold">{value}</div>
      {sub && <div className="mt-1 text-xs text-muted">{sub}</div>}
    </Link>
  );
}
