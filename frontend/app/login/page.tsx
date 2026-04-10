"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { createClient } from "@/lib/supabase/client";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const supabase = createClient();

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);

    const { error } = await supabase.auth.signInWithPassword({
      email,
      password,
    });

    if (error) {
      setError(error.message);
      setLoading(false);
      return;
    }

    router.push("/dashboard");
    router.refresh();
  }

  async function handleMagicLink() {
    if (!email) {
      setError("Introduce tu email para el magic link");
      return;
    }
    setLoading(true);
    const { error } = await supabase.auth.signInWithOtp({ email });
    if (error) {
      setError(error.message);
    } else {
      setError("");
      alert("Revisa tu email para el enlace de acceso");
    }
    setLoading(false);
  }

  async function handleGoogleLogin() {
    const { error } = await supabase.auth.signInWithOAuth({
      provider: "google",
      options: {
        redirectTo: `${window.location.origin}/auth/callback`,
      },
    });
    if (error) setError(error.message);
  }

  return (
    <div className="rounded-xl border border-line bg-panel p-8">
      <h2 className="mb-6 text-xl font-bold">Iniciar sesion</h2>

      <form onSubmit={handleLogin} className="space-y-4">
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
            className="w-full rounded-lg border border-line bg-background px-4 py-2.5 font-mono text-sm text-white outline-none focus:border-accent"
            placeholder="********"
          />
        </div>

        {error && (
          <p className="text-sm text-accent">{error}</p>
        )}

        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-lg bg-accent py-3 text-sm font-bold text-white transition hover:bg-accent-hover disabled:opacity-40"
        >
          {loading ? "Cargando..." : "Entrar"}
        </button>
      </form>

      <div className="my-4 flex items-center gap-3">
        <div className="h-px flex-1 bg-line" />
        <span className="text-xs text-muted">O</span>
        <div className="h-px flex-1 bg-line" />
      </div>

      <div className="space-y-2">
        <button
          onClick={handleMagicLink}
          className="w-full rounded-lg border border-line bg-panel-2 py-2.5 text-sm font-semibold text-muted transition hover:border-accent hover:text-accent"
        >
          Enviar magic link
        </button>

        <button
          onClick={handleGoogleLogin}
          className="w-full rounded-lg border border-line bg-panel-2 py-2.5 text-sm font-semibold text-muted transition hover:border-accent hover:text-accent"
        >
          Continuar con Google
        </button>
      </div>

      <div className="mt-6 flex justify-between text-xs text-muted">
        <Link href="/register" className="hover:text-accent">
          Crear cuenta
        </Link>
        <Link href="/forgot-password" className="hover:text-accent">
          Olvide mi contrasena
        </Link>
      </div>
    </div>
  );
}
