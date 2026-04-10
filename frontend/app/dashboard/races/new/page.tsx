"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";

export default function NewRacePage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setLoading(true);
    const fd = new FormData(e.currentTarget);

    await api.post("/api/races", {
      name: fd.get("name"),
      start_date: fd.get("start_date") || undefined,
      end_date: fd.get("end_date") || undefined,
      category: fd.get("category") || undefined,
      country: fd.get("country") || undefined,
    });

    router.push("/dashboard/races");
  }

  return (
    <div className="mx-auto max-w-xl p-6">
      <h1 className="mb-6 text-2xl font-extrabold">Nueva carrera</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="mb-1 block text-xs font-semibold uppercase tracking-widest text-muted">Nombre</label>
          <input name="name" required className="w-full rounded-lg border border-line bg-background px-4 py-2.5 text-sm text-white outline-none focus:border-accent" />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="mb-1 block text-xs font-semibold uppercase tracking-widest text-muted">Inicio</label>
            <input name="start_date" type="date" className="w-full rounded-lg border border-line bg-background px-4 py-2.5 text-sm text-white" />
          </div>
          <div>
            <label className="mb-1 block text-xs font-semibold uppercase tracking-widest text-muted">Fin</label>
            <input name="end_date" type="date" className="w-full rounded-lg border border-line bg-background px-4 py-2.5 text-sm text-white" />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="mb-1 block text-xs font-semibold uppercase tracking-widest text-muted">Categoria</label>
            <input name="category" placeholder="Grand Tour" className="w-full rounded-lg border border-line bg-background px-4 py-2.5 text-sm text-white outline-none focus:border-accent" />
          </div>
          <div>
            <label className="mb-1 block text-xs font-semibold uppercase tracking-widest text-muted">Pais</label>
            <input name="country" maxLength={3} placeholder="FR" className="w-full rounded-lg border border-line bg-background px-4 py-2.5 text-sm text-white outline-none focus:border-accent" />
          </div>
        </div>
        <button type="submit" disabled={loading} className="w-full rounded-lg bg-accent py-3 text-sm font-bold text-white transition hover:bg-accent-hover disabled:opacity-40">
          {loading ? "Creando..." : "Crear carrera"}
        </button>
      </form>
    </div>
  );
}
