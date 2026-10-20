-- Members can let others send them a message by email from their profile.
-- Only a log of who sent to whom and when is kept (for limits). The message itself is never stored.
ALTER TABLE profiles ADD COLUMN email_open INTEGER NOT NULL DEFAULT 0;

CREATE TABLE profile_emails (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  from_user_id INTEGER NOT NULL,
  to_user_id INTEGER NOT NULL,
  created_at INTEGER NOT NULL
);
CREATE INDEX idx_profile_emails_from ON profile_emails (from_user_id, created_at);
CREATE INDEX idx_profile_emails_pair ON profile_emails (from_user_id, to_user_id, created_at);
CREATE INDEX idx_profile_emails_to ON profile_emails (to_user_id);
