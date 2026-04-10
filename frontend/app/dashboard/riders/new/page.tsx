"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";

export default function NewRiderPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError("");
    setLoading(true);

    const fd = new FormData(e.currentTarget);
    const data: Record<string, unknown> = {
      full_name: fd.get("full_name"),
      nationality: fd.get("nationality") || undefined,
      weight_kg: fd.get("weight_kg") ? Number(fd.get("weight_kg")) : undefined,
      height_cm: fd.get("height_cm") ? Number(fd.get("height_cm")) : undefined,
      ftp_w: fd.get("ftp_w") ? Number(fd.get("ftp_w")) : undefined,
      ftp_wkg: fd.get("ftp_wkg") ? Number(fd.get("ftp_wkg")) : undefined,
      birth_date: fd.get("birth_date") || undefined,
      contract_end: fd.get("contract_end") || undefined,
    };

    try {
      await api.post("/api/riders", data);
      router.push("/dashboard/riders");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-xl p-6">
      <h1 className="mb-6 text-2xl font-extrabold">Nuevo ciclista</h1>

      <form onSubmit={handleSubmit} className="space-y-4">
        <Field label="Nombre completo" name="full_name" required />
        <div className="grid grid-cols-2 gap-4">
          <Field label="Nacionalidad" name="nationality" maxLength={3} placeholder="ES" />
          <Field label="Fecha nacimiento" name="birth_date" type="date" />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <Field label="Peso (kg)" name="weight_kg" type="number" step="0.1" />
          <Field label="Altura (cm)" name="height_cm" type="number" step="0.1" />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <Field label="FTP (W)" name="ftp_w" type="number" />
          <Field label="FTP (W/kg)" name="ftp_wkg" type="number" step="0.01" />
        </div>
        <Field label="Fin de contrato" name="contract_end" type="date" />

        {error && <p className="text-sm text-accent">{error}</p>}

        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-lg bg-accent py-3 text-sm font-bold text-white transition hover:bg-accent-hover disabled:opacity-40"
        >
          {loading ? "Guardando..." : "Crear ciclista"}
        </button>
      </form>
    </div>
  );
}

function Field({
  label,
  name,
  type = "text",
  required = false,
  ...props
}: {
  label: string;
  name: string;
  type?: string;
  required?: boolean;
  [key: string]: unknown;
}) {
  return (
    <div>
      <label className="mb-1 block text-xs font-semibold uppercase tracking-widest text-muted">
        {label}
      </label>
      <input
        name={name}
        type={type}
        required={required}
        className="w-full rounded-lg border border-line bg-background px-4 py-2.5 font-mono text-sm text-white outline-none focus:border-accent"
        {...props}
      />
    </div>
  );
}
