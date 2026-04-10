-- ============================================================
-- Director Hub PRO — Initial Schema
-- ============================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- TEAMS
-- ============================================================
CREATE TABLE teams (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        TEXT NOT NULL,
    slug        TEXT UNIQUE NOT NULL,
    logo_url    TEXT,
    plan        TEXT NOT NULL DEFAULT 'free' CHECK (plan IN ('free', 'pro', 'enterprise')),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================
-- PROFILES (linked to auth.users)
-- ============================================================
CREATE TABLE profiles (
    id          UUID PRIMARY KEY REFERENCES auth.users ON DELETE CASCADE,
    team_id     UUID NOT NULL REFERENCES teams ON DELETE CASCADE,
    full_name   TEXT,
    role        TEXT NOT NULL DEFAULT 'director' CHECK (role IN ('director', 'coach', 'analyst', 'rider')),
    avatar_url  TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_profiles_team_id ON profiles (team_id);

-- ============================================================
-- RIDERS
-- ============================================================
CREATE TABLE riders (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id         UUID NOT NULL REFERENCES teams ON DELETE CASCADE,
    full_name       TEXT NOT NULL,
    birth_date      DATE,
    nationality     TEXT,
    weight_kg       NUMERIC(5,2),
    height_cm       NUMERIC(5,1),
    ftp_w           NUMERIC(6,1),
    ftp_wkg         NUMERIC(4,2),
    vo2max          NUMERIC(4,1),
    contract_end    DATE,
    status          TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'injured', 'inactive')),
    notes           TEXT,
    avatar_url      TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_riders_team_id ON riders (team_id);
CREATE INDEX idx_riders_status ON riders (team_id, status);

-- ============================================================
-- STAGES
-- ============================================================
CREATE TABLE stages (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id         UUID NOT NULL REFERENCES teams ON DELETE CASCADE,
    name            TEXT NOT NULL,
    race_name       TEXT,
    stage_number    INTEGER,
    distance_km     NUMERIC(7,2),
    d_pos_m         NUMERIC(7,1),
    points          INTEGER,
    gpx_url         TEXT,
    thumbnail_url   TEXT,
    race_id         UUID,  -- FK added later via migration when races table exists
    created_by      UUID REFERENCES profiles,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_stages_team_id ON stages (team_id);

-- ============================================================
-- STAGE ANALYSES
-- ============================================================
CREATE TABLE stage_analyses (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    stage_id        UUID NOT NULL REFERENCES stages ON DELETE CASCADE,
    team_id         UUID NOT NULL REFERENCES teams ON DELETE CASCADE,
    rider_id        UUID REFERENCES riders ON DELETE SET NULL,  -- nullable, linked in Fase 2
    analysis_date   DATE,
    start_hour      INTEGER CHECK (start_hour >= 0 AND start_hour <= 23),
    rider_weight_kg NUMERIC(5,2),
    ftp_wkg         NUMERIC(4,2),
    analysis_json   JSONB,
    fig_json        JSONB,
    roadbook        JSONB,
    stats           JSONB,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_stage_analyses_stage ON stage_analyses (stage_id);
CREATE INDEX idx_stage_analyses_team ON stage_analyses (team_id);
CREATE INDEX idx_stage_analyses_rider ON stage_analyses (rider_id);

-- ============================================================
-- WAYPOINTS
-- ============================================================
CREATE TABLE waypoints (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id     UUID NOT NULL REFERENCES stage_analyses ON DELETE CASCADE,
    team_id         UUID NOT NULL REFERENCES teams ON DELETE CASCADE,
    name            TEXT NOT NULL,
    type            TEXT,
    km              NUMERIC(7,2),
    lat             NUMERIC(10,7),
    lon             NUMERIC(10,7),
    alt             NUMERIC(7,1),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_waypoints_analysis ON waypoints (analysis_id);
CREATE INDEX idx_waypoints_team ON waypoints (team_id);

-- ============================================================
-- RACES
-- ============================================================
CREATE TABLE races (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id     UUID NOT NULL REFERENCES teams ON DELETE CASCADE,
    name        TEXT NOT NULL,
    start_date  DATE,
    end_date    DATE,
    category    TEXT,
    country     TEXT,
    status      TEXT NOT NULL DEFAULT 'upcoming' CHECK (status IN ('upcoming', 'ongoing', 'completed', 'cancelled')),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_races_team_id ON races (team_id);
CREATE INDEX idx_races_status ON races (team_id, status);

-- Add FK from stages to races now that races table exists
ALTER TABLE stages
    ADD CONSTRAINT fk_stages_race FOREIGN KEY (race_id) REFERENCES races ON DELETE SET NULL;

-- ============================================================
-- RACE ENTRIES
-- ============================================================
CREATE TABLE race_entries (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    race_id     UUID NOT NULL REFERENCES races ON DELETE CASCADE,
    rider_id    UUID NOT NULL REFERENCES riders ON DELETE CASCADE,
    team_id     UUID NOT NULL REFERENCES teams ON DELETE CASCADE,
    role        TEXT,
    result      TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (race_id, rider_id)
);

CREATE INDEX idx_race_entries_race ON race_entries (race_id);
CREATE INDEX idx_race_entries_rider ON race_entries (rider_id);
CREATE INDEX idx_race_entries_team ON race_entries (team_id);

-- ============================================================
-- PERFORMANCE ENTRIES
-- ============================================================
CREATE TABLE performance_entries (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rider_id            UUID NOT NULL REFERENCES riders ON DELETE CASCADE,
    team_id             UUID NOT NULL REFERENCES teams ON DELETE CASCADE,
    date                DATE NOT NULL,
    type                TEXT,
    distance_km         NUMERIC(7,2),
    duration_min        NUMERIC(7,1),
    avg_power_w         NUMERIC(6,1),
    normalized_power_w  NUMERIC(6,1),
    tss                 NUMERIC(6,1),
    ftp_tested          NUMERIC(6,1),
    notes               TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_perf_rider ON performance_entries (rider_id);
CREATE INDEX idx_perf_team ON performance_entries (team_id);
CREATE INDEX idx_perf_date ON performance_entries (team_id, date);

-- ============================================================
-- FTP HISTORY (for tracking FTP evolution per rider)
-- ============================================================
CREATE TABLE ftp_history (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rider_id    UUID NOT NULL REFERENCES riders ON DELETE CASCADE,
    team_id     UUID NOT NULL REFERENCES teams ON DELETE CASCADE,
    date        DATE NOT NULL,
    ftp_w       NUMERIC(6,1) NOT NULL,
    ftp_wkg     NUMERIC(4,2),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_ftp_history_rider ON ftp_history (rider_id);
CREATE INDEX idx_ftp_history_team ON ftp_history (team_id);

-- ============================================================
-- INVITATIONS (for multi-tenant onboarding)
-- ============================================================
CREATE TABLE invitations (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id     UUID NOT NULL REFERENCES teams ON DELETE CASCADE,
    email       TEXT NOT NULL,
    token_hash  TEXT NOT NULL UNIQUE,
    used        BOOLEAN NOT NULL DEFAULT false,
    expires_at  TIMESTAMPTZ NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_invitations_token ON invitations (token_hash);
CREATE INDEX idx_invitations_team ON invitations (team_id);

-- ============================================================
-- UPDATED_AT TRIGGER FUNCTION
-- ============================================================
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_riders_updated_at
    BEFORE UPDATE ON riders
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trg_races_updated_at
    BEFORE UPDATE ON races
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
