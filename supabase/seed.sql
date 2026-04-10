-- ============================================================
-- Director Hub PRO — Seed Data (Development)
-- ============================================================
-- Two teams with separate users for cross-team isolation testing.
-- NOTE: Users must be created via Supabase Auth first. This seed
-- assumes auth.users rows already exist (created via supabase dashboard
-- or auth API). The UUIDs below are deterministic for testing.

-- ============================================================
-- TEAMS
-- ============================================================
INSERT INTO teams (id, name, slug, logo_url, plan) VALUES
    ('a0000000-0000-0000-0000-000000000001', 'Movistar Team', 'movistar-team', NULL, 'pro'),
    ('b0000000-0000-0000-0000-000000000002', 'INEOS Grenadiers', 'ineos-grenadiers', NULL, 'free');

-- ============================================================
-- PROFILES (linked to auth.users — create these users first)
-- Team A: Movistar
-- Team B: INEOS
-- ============================================================
-- NOTE: These profiles will be auto-created by the on_auth_user_created trigger
-- when users register. For seed purposes, insert directly (assuming auth.users exist).

-- If running locally with Supabase CLI, you can create test users via:
--   supabase auth admin create-user --email director@movistar.test --password test1234
--   supabase auth admin create-user --email coach@movistar.test --password test1234
--   supabase auth admin create-user --email analyst@ineos.test --password test1234
--   supabase auth admin create-user --email rider@ineos.test --password test1234

-- The profiles below use placeholder UUIDs. Replace with actual auth.users IDs after creation.
-- INSERT INTO profiles (id, team_id, full_name, role) VALUES
--     ('<user_uuid_1>', 'a0000000-0000-0000-0000-000000000001', 'Eusebio Unzue', 'director'),
--     ('<user_uuid_2>', 'a0000000-0000-0000-0000-000000000001', 'Patxi Vila', 'coach'),
--     ('<user_uuid_3>', 'b0000000-0000-0000-0000-000000000002', 'Rod Ellingworth', 'analyst'),
--     ('<user_uuid_4>', 'b0000000-0000-0000-0000-000000000002', 'Egan Bernal', 'rider');

-- ============================================================
-- RIDERS — Team A (Movistar)
-- ============================================================
INSERT INTO riders (id, team_id, full_name, birth_date, nationality, weight_kg, height_cm, ftp_w, ftp_wkg, vo2max, contract_end, status, notes) VALUES
    ('c0000000-0000-0000-0000-000000000001', 'a0000000-0000-0000-0000-000000000001',
     'Enric Mas', '1995-01-07', 'ES', 62.0, 176.0, 390, 6.29, 82.0, '2026-12-31', 'active',
     'Lider para grandes vueltas. Escalador puro.'),
    ('c0000000-0000-0000-0000-000000000002', 'a0000000-0000-0000-0000-000000000001',
     'Alex Aranburu', '1995-09-19', 'ES', 68.0, 178.0, 370, 5.44, 76.0, '2026-12-31', 'active',
     'Clasicas y sprints en cuesta.'),
    ('c0000000-0000-0000-0000-000000000003', 'a0000000-0000-0000-0000-000000000001',
     'Oier Lazkano', '1999-05-12', 'ES', 70.0, 182.0, 380, 5.43, 78.0, '2026-06-30', 'active',
     'Joven promesa. Contrato termina pronto.');

-- ============================================================
-- RIDERS — Team B (INEOS)
-- ============================================================
INSERT INTO riders (id, team_id, full_name, birth_date, nationality, weight_kg, height_cm, ftp_w, ftp_wkg, vo2max, contract_end, status, notes) VALUES
    ('d0000000-0000-0000-0000-000000000001', 'b0000000-0000-0000-0000-000000000002',
     'Egan Bernal', '1997-01-13', 'CO', 60.0, 175.0, 400, 6.67, 85.0, '2027-12-31', 'active',
     'Ganador del Tour. Recuperando nivel.'),
    ('d0000000-0000-0000-0000-000000000002', 'b0000000-0000-0000-0000-000000000002',
     'Carlos Rodriguez', '2001-02-02', 'ES', 58.0, 172.0, 365, 6.29, 80.0, '2027-12-31', 'active',
     'Top GC contender.'),
    ('d0000000-0000-0000-0000-000000000003', 'b0000000-0000-0000-0000-000000000002',
     'Tom Pidcock', '1999-07-30', 'GB', 58.0, 170.0, 370, 6.38, 84.0, '2025-12-31', 'injured',
     'Multi-disciplina. Actualmente lesionado.');

-- ============================================================
-- STAGES — Team A sample stages
-- ============================================================
INSERT INTO stages (id, team_id, name, race_name, stage_number, distance_km, d_pos_m, points) VALUES
    ('e0000000-0000-0000-0000-000000000001', 'a0000000-0000-0000-0000-000000000001',
     'Tourmalet', 'Tour de France 2026', 18, 143.5, 4200, 580),
    ('e0000000-0000-0000-0000-000000000002', 'a0000000-0000-0000-0000-000000000001',
     'Angliru', 'Vuelta a Espana 2026', 15, 118.2, 3800, 490),
    ('e0000000-0000-0000-0000-000000000003', 'b0000000-0000-0000-0000-000000000002',
     'Stelvio', 'Giro d''Italia 2026', 20, 168.0, 4500, 620);

-- ============================================================
-- RACES — Sample races
-- ============================================================
INSERT INTO races (id, team_id, name, start_date, end_date, category, country, status) VALUES
    ('f0000000-0000-0000-0000-000000000001', 'a0000000-0000-0000-0000-000000000001',
     'Tour de France 2026', '2026-07-04', '2026-07-26', 'Grand Tour', 'FR', 'upcoming'),
    ('f0000000-0000-0000-0000-000000000002', 'b0000000-0000-0000-0000-000000000002',
     'Giro d''Italia 2026', '2026-05-09', '2026-05-31', 'Grand Tour', 'IT', 'upcoming');

-- ============================================================
-- FTP HISTORY — Sample entries
-- ============================================================
INSERT INTO ftp_history (rider_id, team_id, date, ftp_w, ftp_wkg) VALUES
    ('c0000000-0000-0000-0000-000000000001', 'a0000000-0000-0000-0000-000000000001', '2026-01-15', 380, 6.13),
    ('c0000000-0000-0000-0000-000000000001', 'a0000000-0000-0000-0000-000000000001', '2026-03-01', 390, 6.29),
    ('d0000000-0000-0000-0000-000000000001', 'b0000000-0000-0000-0000-000000000002', '2026-02-01', 390, 6.50),
    ('d0000000-0000-0000-0000-000000000001', 'b0000000-0000-0000-0000-000000000002', '2026-03-15', 400, 6.67);
