-- City and country for each profile. Existing profiles keep working with blanks until their owner edits and resubmits.
ALTER TABLE profiles ADD COLUMN city TEXT NOT NULL DEFAULT '';
ALTER TABLE profiles ADD COLUMN country TEXT NOT NULL DEFAULT '';
