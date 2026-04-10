"use client";

import { useState } from "react";
import Link from "next/link";
import { createClient } from "@/lib/supabase/client";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);

  const supabase = createClient();

  async function handleReset(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);

    const { error } = await supabase.auth.resetPasswordForEmail(email, {
      redirectTo: `${window.location.origin}/auth/callback`,
    });

    if (error) {
      setError(error.message);
    } else {
      setSent(true);
    }
    setLoading(false);
  }

  if (sent) {
    return (
      <div className="rounded-xl border border-line bg-panel p-8 text-center">
        <h2 className="mb-4 text-xl font-bold">Email enviado</h2>
        <p className="text-sm text-muted">
          Si existe una cuenta con <strong>{email}</strong>, recibiras un enlace
          para restablecer tu contrasena.
        </p>
        <Link
          href="/login"
          className="mt-6 inline-block text-sm text-accent hover:underline"
        >
          Volver al login
        </Link>
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-line bg-panel p-8">
      <h2 className="mb-6 text-xl font-bold">Recuperar contrasena</h2>

      <form onSubmit={handleReset} className="space-y-4">
        <div>
          <label className="mb-1 block text-xs font-semibold uppercase tracking-widest text-muted">
            Email
          </label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="w-full rounded-lg border border-line bg-background px-4 py-2.5 font-mono text-sm text-white outline-none focus:border-accent"
            placeholder="tu@email.com"
          />
        </div>

        {error && <p className="text-sm text-accent">{error}</p>}

        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-lg bg-accent py-3 text-sm font-bold text-white transition hover:bg-accent-hover disabled:opacity-40"
        >
          {loading ? "Enviando..." : "Enviar enlace de recuperacion"}
        </button>
      </form>

      <p className="mt-6 text-center text-xs text-muted">
        <Link href="/login" className="text-accent hover:underline">
          Volver al login
        </Link>
      </p>
    </div>
  );
}
