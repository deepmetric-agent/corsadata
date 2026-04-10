"use client";

import { useRouter } from "next/navigation";
import { createClient } from "@/lib/supabase/client";

export function LogoutButton() {
  const router = useRouter();
  const supabase = createClient();

  async function handleLogout() {
    await supabase.auth.signOut();
    router.push("/login");
    router.refresh();
  }

  return (
    <button
      onClick={handleLogout}
      className="rounded-lg border border-line bg-panel px-3 py-1.5 text-xs font-semibold text-muted transition hover:border-accent hover:text-accent"
    >
      Salir
    </button>
  );
}
