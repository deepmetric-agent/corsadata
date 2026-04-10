-- ============================================================
-- Director Hub PRO — Row Level Security Policies
-- ============================================================

-- Enable RLS on ALL tables
ALTER TABLE teams ENABLE ROW LEVEL SECURITY;
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE riders ENABLE ROW LEVEL SECURITY;
ALTER TABLE stages ENABLE ROW LEVEL SECURITY;
ALTER TABLE stage_analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE waypoints ENABLE ROW LEVEL SECURITY;
ALTER TABLE races ENABLE ROW LEVEL SECURITY;
ALTER TABLE race_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE performance_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE ftp_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE invitations ENABLE ROW LEVEL SECURITY;

-- ============================================================
-- HELPER: get current user's team_id
-- ============================================================
CREATE OR REPLACE FUNCTION public.get_my_team_id()
RETURNS UUID AS $$
    SELECT team_id FROM profiles WHERE id = auth.uid()
$$ LANGUAGE sql SECURITY DEFINER STABLE;

-- ============================================================
-- TEAMS — user can only see their own team
-- ============================================================
CREATE POLICY "team_isolation" ON teams
    FOR ALL USING (id = public.get_my_team_id());

-- ============================================================
-- PROFILES — user can only see profiles in their team
-- ============================================================
CREATE POLICY "team_isolation" ON profiles
    FOR ALL USING (team_id = public.get_my_team_id());

-- Allow insert during signup (user has no profile yet)
CREATE POLICY "allow_insert_own_profile" ON profiles
    FOR INSERT WITH CHECK (id = auth.uid());

-- ============================================================
-- STANDARD team_isolation POLICIES (all other tables)
-- ============================================================
CREATE POLICY "team_isolation" ON riders
    FOR ALL USING (team_id = public.get_my_team_id());

CREATE POLICY "team_isolation" ON stages
    FOR ALL USING (team_id = public.get_my_team_id());

CREATE POLICY "team_isolation" ON stage_analyses
    FOR ALL USING (team_id = public.get_my_team_id());

CREATE POLICY "team_isolation" ON waypoints
    FOR ALL USING (team_id = public.get_my_team_id());

CREATE POLICY "team_isolation" ON races
    FOR ALL USING (team_id = public.get_my_team_id());

CREATE POLICY "team_isolation" ON race_entries
    FOR ALL USING (team_id = public.get_my_team_id());

CREATE POLICY "team_isolation" ON performance_entries
    FOR ALL USING (team_id = public.get_my_team_id());

CREATE POLICY "team_isolation" ON ftp_history
    FOR ALL USING (team_id = public.get_my_team_id());

CREATE POLICY "team_isolation" ON invitations
    FOR ALL USING (team_id = public.get_my_team_id());

-- ============================================================
-- AUTO-CREATE PROFILE ON SIGNUP
-- This trigger creates a profile row when a new user signs up.
-- The team_id comes from user metadata set during registration.
-- ============================================================
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
DECLARE
    v_team_id UUID;
    v_email_prefix TEXT;
BEGIN
    IF (NEW.raw_user_meta_data ->> 'team_id') IS NOT NULL THEN
        -- Invitation flow: join existing team
        v_team_id := (NEW.raw_user_meta_data ->> 'team_id')::UUID;
    ELSE
        -- New signup: auto-create a team for this director
        v_email_prefix := split_part(NEW.email, '@', 1);
        INSERT INTO public.teams (name, slug)
        VALUES (
            COALESCE(NEW.raw_user_meta_data ->> 'team_name', 'Mi Equipo'),
            'team-' || substr(replace(NEW.id::text, '-', ''), 1, 8)
        )
        RETURNING id INTO v_team_id;
    END IF;

    INSERT INTO public.profiles (id, team_id, full_name, role)
    VALUES (
        NEW.id,
        v_team_id,
        COALESCE(NEW.raw_user_meta_data ->> 'full_name', v_email_prefix, ''),
        COALESCE(NEW.raw_user_meta_data ->> 'role', 'director')
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();
