-- Marks made-up sample profiles (seed/sample-profiles.json). Sample profiles are only loaded into local or staging databases.
-- The live site refuses to show a sample profile or its photo unless ALLOW_SAMPLES is set to 1.
ALTER TABLE profiles ADD COLUMN is_sample INTEGER NOT NULL DEFAULT 0;
