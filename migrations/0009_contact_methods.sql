-- Members can now share several contact methods (social accounts, phone, email), not just one.
-- contact_methods is a JSON array, for example [{"kind":"instagram","value":"sam_t"},{"kind":"email","value":"sam@example.com"}].
-- kind: instagram | facebook | tiktok | snapchat | x | whatsapp | phone | email
-- Still private. Shown only to members the owner says yes to (see contact_requests).
ALTER TABLE profiles ADD COLUMN contact_methods TEXT NOT NULL DEFAULT '[]';

-- Carry over anything saved with the single-detail version.
UPDATE profiles
SET contact_methods = json_array(json_object('kind', contact_kind, 'value', contact_value))
WHERE contact_kind != '' AND contact_value != '';

ALTER TABLE profiles DROP COLUMN contact_kind;
ALTER TABLE profiles DROP COLUMN contact_value;
