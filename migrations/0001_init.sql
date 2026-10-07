CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT NOT NULL UNIQUE,
  pass_hash TEXT NOT NULL,
  pass_salt TEXT NOT NULL,
  is_admin INTEGER NOT NULL DEFAULT 0,
  created_at INTEGER NOT NULL
);

CREATE TABLE sessions (
  token_hash TEXT PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  expires_at INTEGER NOT NULL
);

CREATE TABLE profiles (
  user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  stub TEXT UNIQUE,
  first_name TEXT NOT NULL DEFAULT '',
  age INTEGER,
  suburb TEXT NOT NULL DEFAULT '',
  occupation TEXT NOT NULL DEFAULT '',
  training TEXT NOT NULL DEFAULT '',
  about TEXT NOT NULL DEFAULT '',
  looking_for TEXT NOT NULL DEFAULT '',
  status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft','pending','approved','rejected')),
  admin_note TEXT NOT NULL DEFAULT '',
  submitted_at INTEGER,
  updated_at INTEGER NOT NULL
);

CREATE TABLE photos (
  id TEXT PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  content_type TEXT NOT NULL,
  position INTEGER NOT NULL DEFAULT 0,
  created_at INTEGER NOT NULL
);
CREATE INDEX photos_user ON photos(user_id, position);

CREATE TABLE login_attempts (
  email TEXT NOT NULL,
  at INTEGER NOT NULL
);
CREATE INDEX login_attempts_email ON login_attempts(email, at);
