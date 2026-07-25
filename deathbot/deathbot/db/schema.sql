-- ===========================================================================
-- DeathBot SQLite schema
-- ===========================================================================
PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY,          -- Telegram user id
    username      TEXT,
    full_name     TEXT,
    role          TEXT NOT NULL DEFAULT 'guest',
    is_active     INTEGER NOT NULL DEFAULT 1,
    is_banned     INTEGER NOT NULL DEFAULT 0,
    created_at    TEXT NOT NULL DEFAULT (datetime('now')),
    last_seen_at  TEXT
);

CREATE TABLE IF NOT EXISTS roles (
    name          TEXT PRIMARY KEY,
    description   TEXT
);

CREATE TABLE IF NOT EXISTS invites (
    code          TEXT PRIMARY KEY,
    role          TEXT NOT NULL DEFAULT 'user',
    created_by    INTEGER,
    used_by       INTEGER,
    used_at       TEXT,
    expires_at    TEXT,
    created_at    TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS api_keys (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id       INTEGER NOT NULL,
    provider      TEXT NOT NULL,
    ciphertext    TEXT NOT NULL,               -- AES-256-GCM encrypted
    created_at    TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(user_id, provider),
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS notes (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id       INTEGER NOT NULL,
    title         TEXT,
    body          TEXT NOT NULL DEFAULT '',
    created_at    TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at    TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS todos (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id       INTEGER NOT NULL,
    text          TEXT NOT NULL,
    done          INTEGER NOT NULL DEFAULT 0,
    created_at    TEXT NOT NULL DEFAULT (datetime('now')),
    completed_at  TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS settings (
    user_id       INTEGER NOT NULL,
    key           TEXT NOT NULL,
    value         TEXT,
    PRIMARY KEY(user_id, key),
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id       INTEGER,
    action        TEXT NOT NULL,
    detail        TEXT,
    created_at    TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS ai_history (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id       INTEGER NOT NULL,
    role          TEXT NOT NULL,               -- user | assistant | system
    content       TEXT NOT NULL,
    provider      TEXT,
    model         TEXT,
    created_at    TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS provider_usage (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id       INTEGER,
    provider      TEXT NOT NULL,
    model         TEXT,
    tokens        INTEGER NOT NULL DEFAULT 0,
    created_at    TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS cache (
    key           TEXT PRIMARY KEY,
    value         TEXT,
    expires_at    TEXT
);

CREATE INDEX IF NOT EXISTS idx_notes_user   ON notes(user_id);
CREATE INDEX IF NOT EXISTS idx_todos_user   ON todos(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_user   ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_history_user ON ai_history(user_id);
