-- Messages sent through the contact form. Kept so nothing is lost if email delivery fails.
CREATE TABLE contact_messages (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  email TEXT NOT NULL,
  message TEXT NOT NULL,
  ip_hash TEXT NOT NULL,
  emailed INTEGER NOT NULL DEFAULT 0,
  created_at INTEGER NOT NULL
);
CREATE INDEX contact_messages_ip ON contact_messages(ip_hash, created_at);
