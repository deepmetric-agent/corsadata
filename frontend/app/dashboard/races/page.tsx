"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import type { Race } from "@/types/database";

export default function RacesPage() {
  const [races, setRaces] = useState<Race[]>([]);

  useEffect(() => {
    api.get<Race[]>("/api/races").then(setRaces).catch(() => {});
  }, []);

  const STATUS_COLORS: Record<string, string> = {
    upcoming: "text-accent",
    ongoing: "text-green-ok",
    completed: "text-muted",
    cancelled: "text-muted line-through",
  };

  // Group by month
  const byMonth: Record<string, Race[]> = {};
  races.forEach((r) => {
    const month = r.start_date?.slice(0, 7) || "Sin fecha";
    if (!byMonth[month]) byMonth[month] = [];
    byMonth[month].push(r);
  });

  return (
    <div className="p-6">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-extrabold">Carreras</h1>
        <Link
          href="/dashboard/races/new"
          className="rounded-lg bg-accent px-4 py-2 text-sm font-bold text-white transition hover:bg-accent-hover"
        >
          + Nueva carrera
        </Link>
      </div>

      {Object.entries(byMonth)
        .sort()
        .map(([month, monthRaces]) => (
          <div key={month} className="mb-6">
            <h2 className="mb-3 text-sm font-bold uppercase tracking-wider text-muted">
              {month}
            </h2>
            <div className="space-y-2">
              {monthRaces.map((race) => (
                <Link
                  key={race.id}
                  href={`/dashboard/races/${race.id}`}
                  className="flex items-center justify-between rounded-xl border border-line bg-panel p-4 transition hover:border-accent"
                >
                  <div>
                    <div className="font-bold">{race.name}</div>
                    <div className="text-xs text-muted">
                      {race.start_date || "?"} → {race.end_date || "?"} · {race.country || "—"} · {race.category || ""}
                    </div>
                  </div>
                  <span className={`text-xs font-semibold ${STATUS_COLORS[race.status] || ""}`}>
                    {race.status.toUpperCase()}
                  </span>
                </Link>
              ))}
            </div>
          </div>
        ))}

      {races.length === 0 && (
        <div className="py-20 text-center text-muted">No hay carreras registradas</div>
      )}
    </div>
  );
}
