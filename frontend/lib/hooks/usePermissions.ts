import { useEffect, useState } from "react";
import { createClient } from "@/lib/supabase/client";
import type { Role } from "@/types/database";

const ROLE_PERMISSIONS: Record<Role, Set<string>> = {
  director: new Set(["manage_team", "manage_billing", "crud_riders", "crud_races", "run_analysis", "view_all"]),
  coach: new Set(["crud_riders", "crud_races", "run_analysis", "view_all"]),
  analyst: new Set(["run_analysis", "view_all"]),
  rider: new Set(["view_own"]),
};

export function usePermissions() {
  const [role, setRole] = useState<Role>("rider");

  useEffect(() => {
    const supabase = createClient();
    supabase.auth.getUser().then(async ({ data: { user } }) => {
      if (!user) return;
      const { data } = await supabase
        .from("profiles")
        .select("role")
        .eq("id", user.id)
        .single();
      if (data?.role) setRole(data.role as Role);
    });
  }, []);

  const perms = ROLE_PERMISSIONS[role] || ROLE_PERMISSIONS.rider;

  return {
    role,
    canManageTeam: perms.has("manage_team"),
    canManageBilling: perms.has("manage_billing"),
    canCrudRiders: perms.has("crud_riders"),
    canCrudRaces: perms.has("crud_races"),
    canRunAnalysis: perms.has("run_analysis"),
    canViewAll: perms.has("view_all"),
    hasPermission: (perm: string) => perms.has(perm),
  };
}
