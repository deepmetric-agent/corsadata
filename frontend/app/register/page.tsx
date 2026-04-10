"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { createClient } from "@/lib/supabase/client";

export default function RegisterPage() {
  const router = useRouter();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const supabase = createClient();

  async function handleRegister(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);

    const { error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: {
          full_name: fullName,
          role: "director",
        },
        emailRedirectTo: `${window.location.origin}/auth/confirm`,
      },
    });

    if (error) {
      setError(error.message);
      setLoading(false);
      return;
    }

    setSuccess(true);
    setLoading(false);
  }

  if (success) {
    return (
      <div className="rounded-xl border border-line bg-panel p-8 text-center">
        <h2 className="mb-4 text-xl font-bold">Verifica tu email</h2>
        <p className="text-sm text-muted">
          Hemos enviado un enlace de verificacion a <strong>{email}</strong>.
          Revisa tu bandeja de entrada para activar tu cuenta.
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
      <h2 className="mb-6 text-xl font-bold">Crear cuenta</h2>

      <form onSubmit={handleRegister} className="space-y-4">
        <div>
          <label className="mb-1 block text-xs font-semibold uppercase tracking-widest text-muted">
            Nombre completo
          </label>
          <input
            type="text"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            required
            className="w-full rounded-lg border border-line bg-background px-4 py-2.5 font-mono text-sm text-white outline-none focus:border-accent"
            placeholder="Tu nombre"
          />
        </div>

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

        <div>
          <label className="mb-1 block text-xs font-semibold uppercase tracking-widest text-muted">
            Contrasena
          </label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={8}
            className="w-full rounded-lg border border-line bg-background px-4 py-2.5 font-mono text-sm text-white outline-none focus:border-accent"
            placeholder="Min. 8 caracteres"
          />
        </div>

        {error && <p className="text-sm text-accent">{error}</p>}

        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-lg bg-accent py-3 text-sm font-bold text-white transition hover:bg-accent-hover disabled:opacity-40"
        >
          {loading ? "Creando cuenta..." : "Crear cuenta"}
        </button>
      </form>

      <p className="mt-6 text-center text-xs text-muted">
        Ya tienes cuenta?{" "}
        <Link href="/login" className="text-accent hover:underline">
          Iniciar sesion
        </Link>
      </p>
    </div>
  );
}
