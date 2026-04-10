"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { Profile, Team } from "@/types/database";

export default function SettingsPage() {
  const [team, setTeam] = useState<Team | null>(null);
  const [members, setMembers] = useState<Profile[]>([]);

  useEffect(() => {
    api.get<Team>("/api/teams/me").then(setTeam).catch(() => {});
    api.get<Profile[]>("/api/teams/members").then(setMembers).catch(() => {});
  }, []);

  const [email, setEmail] = useState("");
  const [inviteResult, setInviteResult] = useState("");

  async function sendInvite() {
    if (!email) return;
    try {
      await api.post("/api/teams/invite", { email });
      setInviteResult("Invitacion enviada");
      setEmail("");
    } catch (e) {
      setInviteResult(e instanceof Error ? e.message : "Error");
    }
  }

  return (
    <div className="mx-auto max-w-2xl p-6">
      <h1 className="mb-6 text-2xl font-extrabold">Configuracion del equipo</h1>

      {/* Team info */}
      {team && (
        <div className="mb-6 rounded-xl border border-line bg-panel p-4">
          <div className="text-lg font-bold">{team.name}</div>
          <div className="text-xs text-muted">
            Slug: {team.slug} · Plan: {team.plan.toUpperCase()}
          </div>
        </div>
      )}

      {/* Members */}
      <div className="mb-6">
        <h2 className="mb-3 text-sm font-bold uppercase tracking-wider text-muted">
          Miembros ({members.length})
        </h2>
        <div className="space-y-1.5">
          {members.map((m) => (
            <div
              key={m.id}
              className="flex items-center justify-between rounded-lg border border-line bg-panel-2 px-4 py-2.5"
            >
              <span className="font-semibold">{m.full_name || "Sin nombre"}</span>
              <span className="text-xs font-semibold uppercase text-muted">{m.role}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Invite */}
      <div className="rounded-xl border border-line bg-panel p-4">
        <h2 className="mb-3 text-sm font-bold uppercase tracking-wider text-muted">
          Invitar miembro
        </h2>
        <div className="flex gap-2">
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="email@equipo.com"
            className="flex-1 rounded-lg border border-line bg-background px-4 py-2 text-sm text-white outline-none focus:border-accent"
          />
          <button
            onClick={sendInvite}
            className="rounded-lg bg-accent px-4 py-2 text-sm font-bold text-white transition hover:bg-accent-hover"
          >
            Invitar
          </button>
        </div>
        {inviteResult && (
          <p className="mt-2 text-xs text-muted">{inviteResult}</p>
        )}
      </div>
    </div>
  );
}
