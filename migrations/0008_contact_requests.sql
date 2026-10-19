-- Contact requests. A member can keep one private contact detail (contact_kind + contact_value).
-- It is never shown on the profile. A member with a live profile can ask for it, and the owner says yes or no.
-- contact_kind: instagram | snapchat | whatsapp | phone | email
-- contact_open: 1 when the member lets others ask. Off by default.
ALTER TABLE profiles ADD COLUMN contact_kind TEXT NOT NULL DEFAULT '';
ALTER TABLE profiles ADD COLUMN contact_value TEXT NOT NULL DEFAULT '';
ALTER TABLE profiles ADD COLUMN contact_open INTEGER NOT NULL DEFAULT 0;

-- One row per pair, so nobody can ask the same member twice.
-- status: pending (waiting), approved (owner shared it), declined (owner said no or stopped sharing), blocked (owner blocked them).
-- The person asking only ever sees "Requested" until approved, so a no is never announced.
CREATE TABLE contact_requests (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  from_user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  to_user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending','approved','declined','blocked')),
  created_at INTEGER NOT NULL,
  decided_at INTEGER,
  UNIQUE (from_user_id, to_user_id)
);
CREATE INDEX contact_requests_to ON contact_requests(to_user_id, status, created_at);
CREATE INDEX contact_requests_from ON contact_requests(from_user_id, created_at);
