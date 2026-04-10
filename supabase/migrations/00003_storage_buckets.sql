-- ============================================================
-- Director Hub PRO — Storage Buckets
-- ============================================================

-- GPX files bucket (private — access only via signed URLs)
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
    'gpx-files',
    'gpx-files',
    false,
    52428800,  -- 50MB
    ARRAY['application/gpx+xml', 'application/xml', 'text/xml', 'application/octet-stream']
);

-- Avatars bucket (public read, authenticated write)
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
    'avatars',
    'avatars',
    true,
    5242880,  -- 5MB
    ARRAY['image/jpeg', 'image/png', 'image/webp']
);

-- ============================================================
-- STORAGE POLICIES — gpx-files (private)
-- ============================================================

-- Authenticated users can upload to their team's folder
CREATE POLICY "gpx_upload" ON storage.objects
    FOR INSERT TO authenticated
    WITH CHECK (
        bucket_id = 'gpx-files'
        AND (storage.foldername(name))[1] = public.get_my_team_id()::text
    );

-- Authenticated users can read their team's files
CREATE POLICY "gpx_read" ON storage.objects
    FOR SELECT TO authenticated
    USING (
        bucket_id = 'gpx-files'
        AND (storage.foldername(name))[1] = public.get_my_team_id()::text
    );

-- Authenticated users can delete their team's files
CREATE POLICY "gpx_delete" ON storage.objects
    FOR DELETE TO authenticated
    USING (
        bucket_id = 'gpx-files'
        AND (storage.foldername(name))[1] = public.get_my_team_id()::text
    );

-- ============================================================
-- STORAGE POLICIES — avatars (public read, auth write)
-- ============================================================

-- Anyone can read avatars (public bucket)
CREATE POLICY "avatars_public_read" ON storage.objects
    FOR SELECT TO public
    USING (bucket_id = 'avatars');

-- Authenticated users can upload to their team's folder
CREATE POLICY "avatars_upload" ON storage.objects
    FOR INSERT TO authenticated
    WITH CHECK (
        bucket_id = 'avatars'
        AND (storage.foldername(name))[1] = public.get_my_team_id()::text
    );

-- Authenticated users can update their team's avatars
CREATE POLICY "avatars_update" ON storage.objects
    FOR UPDATE TO authenticated
    USING (
        bucket_id = 'avatars'
        AND (storage.foldername(name))[1] = public.get_my_team_id()::text
    );

-- Authenticated users can delete their team's avatars
CREATE POLICY "avatars_delete" ON storage.objects
    FOR DELETE TO authenticated
    USING (
        bucket_id = 'avatars'
        AND (storage.foldername(name))[1] = public.get_my_team_id()::text
    );
