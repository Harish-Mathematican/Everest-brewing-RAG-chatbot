import sqlite3
import os
import json
import time
from typing import List, Dict, Any, Optional, Tuple

DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_DIR, "everest.db")
SCHEMA_PATH = os.path.join(DB_DIR, "schema.sql")

class EverestDB:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with self.get_connection() as conn:
            if os.path.exists(SCHEMA_PATH):
                with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
                    conn.executescript(f.read())
            conn.commit()

    def log_chat(self, session_id: str, query: str, department: str, answer: str, confidence: float, sources: List[Dict[str, Any]], exec_ms: float):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        sources_json = json.dumps(sources)
        with self.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO chat_history (session_id, timestamp, query, department, answer, confidence, sources_json, exec_ms)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (session_id, timestamp, query, department, answer, confidence, sources_json, exec_ms)
            )
            conn.commit()

    def get_chat_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM chat_history ORDER BY id DESC LIMIT ?", (limit,))
            return [dict(row) for row in cursor.fetchall()]

    def log_telemetry(self, department: str, metric_key: str, metric_value: float):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with self.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO telemetry_log (timestamp, department, metric_key, metric_value)
                VALUES (?, ?, ?, ?)
                """,
                (timestamp, department, metric_key, metric_value)
            )
            conn.commit()

    def get_telemetry_history(self, metric_key: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            if metric_key:
                cursor = conn.execute("SELECT * FROM telemetry_log WHERE metric_key = ? ORDER BY id DESC LIMIT ?", (metric_key, limit))
            else:
                cursor = conn.execute("SELECT * FROM telemetry_log ORDER BY id DESC LIMIT ?", (limit,))
            return [dict(row) for row in cursor.fetchall()]

    def insert_ingested_document(self, doc_id: str, department: str, title: str, subsection: str, content: str) -> bool:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with self.get_connection() as conn:
            try:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO ingested_documents (doc_id, department, title, subsection, content, ingested_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (doc_id, department, title, subsection, content, timestamp)
                )
                conn.commit()
                return True
            except Exception:
                return False

    def get_ingested_documents(self) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM ingested_documents ORDER BY id DESC")
            return [dict(row) for row in cursor.fetchall()]

    def insert_incident_report(self, report_id: str, employee_id: str, department: str, hazard_type: str, location: str, description: str, severity: str = "LOW") -> bool:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with self.get_connection() as conn:
            try:
                conn.execute(
                    """
                    INSERT INTO incident_reports (report_id, timestamp, employee_id, department, hazard_type, location, description, severity, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'OPEN_INVESTIGATION')
                    """,
                    (report_id, timestamp, employee_id, department, hazard_type, location, description, severity)
                )
                conn.commit()
                return True
            except Exception:
                return False

    def get_incident_reports(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM incident_reports ORDER BY id DESC LIMIT ?", (limit,))
            return [dict(row) for row in cursor.fetchall()]

    def insert_quality_rework(self, ncr_id: str, batch_id: str, line_or_tank: str, defect_type: str, parameter: str, action_taken: str, status: str = "IN_REWORK") -> bool:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with self.get_connection() as conn:
            try:
                conn.execute(
                    """
                    INSERT INTO quality_rework_log (ncr_id, timestamp, batch_id, line_or_tank, defect_type, parameter, action_taken, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (ncr_id, timestamp, batch_id, line_or_tank, defect_type, parameter, action_taken, status)
                )
                conn.commit()
                return True
            except Exception:
                return False

    def get_quality_rework_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM quality_rework_log ORDER BY id DESC LIMIT ?", (limit,))
            return [dict(row) for row in cursor.fetchall()]

    def run_custom_query(self, sql_query: str) -> Tuple[List[str], List[List[Any]]]:
        with self.get_connection() as conn:
            cursor = conn.execute(sql_query)
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            rows = cursor.fetchall()
            return columns, [list(r) for r in rows]
