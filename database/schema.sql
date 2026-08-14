-- Everest Brewing RAG Platform — SQLite Schema
-- Run automatically on startup via everest_db.py

CREATE TABLE IF NOT EXISTS chat_history (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id   TEXT    NOT NULL,
    timestamp    TEXT    NOT NULL,
    query        TEXT    NOT NULL,
    department   TEXT    NOT NULL DEFAULT 'All',
    answer       TEXT    NOT NULL,
    confidence   REAL    NOT NULL DEFAULT 0.0,
    sources_json TEXT    NOT NULL DEFAULT '[]',
    exec_ms      REAL    NOT NULL DEFAULT 0.0
);

CREATE TABLE IF NOT EXISTS telemetry_log (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp    TEXT    NOT NULL,
    department   TEXT    NOT NULL,
    metric_key   TEXT    NOT NULL,
    metric_value REAL    NOT NULL
);

CREATE TABLE IF NOT EXISTS ingested_documents (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    doc_id       TEXT    NOT NULL UNIQUE,
    department   TEXT    NOT NULL,
    title        TEXT    NOT NULL,
    subsection   TEXT    NOT NULL DEFAULT 'Live Operations',
    content      TEXT    NOT NULL,
    ingested_at  TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS incident_reports (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id    TEXT    NOT NULL UNIQUE,
    timestamp    TEXT    NOT NULL,
    employee_id  TEXT    NOT NULL,
    department   TEXT    NOT NULL,
    hazard_type  TEXT    NOT NULL,
    location     TEXT    NOT NULL,
    description  TEXT    NOT NULL,
    severity     TEXT    NOT NULL DEFAULT 'LOW',
    status       TEXT    NOT NULL DEFAULT 'OPEN_INVESTIGATION'
);

CREATE TABLE IF NOT EXISTS quality_rework_log (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    ncr_id       TEXT    NOT NULL UNIQUE,
    timestamp    TEXT    NOT NULL,
    batch_id     TEXT    NOT NULL,
    line_or_tank TEXT    NOT NULL,
    defect_type  TEXT    NOT NULL,
    parameter    TEXT    NOT NULL,
    action_taken TEXT    NOT NULL,
    status       TEXT    NOT NULL DEFAULT 'IN_REWORK'
);
