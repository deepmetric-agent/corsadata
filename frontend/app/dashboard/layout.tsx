import Link from "next/link";
import { createClient } from "@/lib/supabase/server";
import { redirect } from "next/navigation";
import { LogoutButton } from "@/components/layout/LogoutButton";

export default async function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) redirect("/login");

  const { data: profile } = await supabase
    .from("profiles")
    .select("full_name, role, team_id")
    .eq("id", user.id)
    .single();

  return (
    <div className="flex h-screen flex-col overflow-hidden">
      {/* TOPBAR */}
      <header className="flex h-[52px] flex-shrink-0 items-center gap-4 border-b border-line bg-panel px-5">
        <Link href="/dashboard" className="text-xl font-extrabold tracking-tight">
          DIRECTOR <span className="text-accent">HUB</span> PRO
        </Link>

        <nav className="ml-5 flex gap-1">
          <NavTab href="/dashboard/stages">Etapas</NavTab>
          <NavTab href="/dashboard/riders">Ciclistas</NavTab>
          <NavTab href="/dashboard/races">Carreras</NavTab>
          <NavTab href="/dashboard/performance">Rendimiento</NavTab>
        </nav>

        <div className="ml-auto flex items-center gap-3">
          <span className="text-xs text-muted">
            {profile?.full_name || user.email}
          </span>
          <LogoutButton />
        </div>
      </header>

      {/* MAIN CONTENT */}
      <main className="flex-1 overflow-auto">{children}</main>
    </div>
  );
}

function NavTab({ href, children }: { href: string; children: React.ReactNode }) {
  return (
    <Link
      href={href}
      className="rounded-lg px-4 py-1.5 text-xs font-semibold uppercase tracking-wider text-muted transition hover:bg-panel-2 hover:text-white"
    >
      {children}
    </Link>
  );
}
