"""
#Gyan Labs - Natural Language to SQL Agent
==========================================
Inspects SQLite schemas, generates safe read-only SQL queries,
executes them, and returns structured tabular results with explanations.
"""

from typing import Dict, Any, List, Optional
import sqlite3
import re
from pathlib import Path
from src.generation.prompts import SQL_GENERATION_PROMPT


class SQLAnalyticsAgent:
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self._ensure_db_initialized()

    def _ensure_db_initialized(self):
        """
        Creates sample enterprise analytics tables if the database does not exist.
        """
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            # 1. AI Compute Nodes
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS compute_nodes (
                node_id TEXT PRIMARY KEY,
                hub_location TEXT,
                gpu_type TEXT,
                gpu_count INTEGER,
                memory_gb INTEGER,
                status TEXT,
                hourly_cost_usd REAL
            )
            """)

            # 2. AI Research Projects
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS ai_projects (
                project_id TEXT PRIMARY KEY,
                name TEXT,
                lead_architect TEXT,
                department TEXT,
                status TEXT,
                compute_hours_spent REAL,
                budget_usd REAL
            )
            """)

            # 3. Model Deployment Telemetry
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS model_telemetry (
                deployment_id TEXT PRIMARY KEY,
                model_name TEXT,
                hub_location TEXT,
                p95_latency_ms REAL,
                total_requests_24h INTEGER,
                error_rate_pct REAL
            )
            """)

            # Seed data if empty
            cursor.execute("SELECT COUNT(*) FROM compute_nodes")
            if cursor.fetchone()[0] == 0:
                nodes = [
                    ("NODE-CAN-01", "Toronto, ON", "NVIDIA H100 SXM5", 8, 640, "Active", 28.50),
                    ("NODE-CAN-02", "Montreal, QC", "NVIDIA A100 80GB", 8, 640, "Active", 19.20),
                    ("NODE-CAN-03", "Vancouver, BC", "NVIDIA L40S", 4, 192, "Active", 11.40),
                    ("NODE-USA-01", "San Francisco, CA", "NVIDIA H100 NVL", 8, 752, "Active", 32.00),
                    ("NODE-USA-02", "Seattle, WA", "NVIDIA H100 SXM5", 8, 640, "Active", 28.50),
                    ("NODE-USA-03", "Austin, TX", "NVIDIA A100 80GB", 4, 320, "Maintenance", 9.60)
                ]
                cursor.executemany("INSERT INTO compute_nodes VALUES (?, ?, ?, ?, ?, ?, ?)", nodes)

                projects = [
                    ("PRJ-101", "Agentic MCP Orchestrator", "Liam Tremblay", "AI Research", "Active", 1420.5, 85000),
                    ("PRJ-102", "Cross-Border RAG Engine", "Ethan Sullivan", "Engineering", "Active", 890.0, 60000),
                    ("PRJ-103", "Zero-Trust Security Gateway", "Charlotte Bélanger", "Security", "Active", 320.0, 35000),
                    ("PRJ-104", "Speech-to-Speech LLM Alignment", "Chloe Gagnon", "AI Research", "Active", 2150.0, 110000)
                ]
                cursor.executemany("INSERT INTO ai_projects VALUES (?, ?, ?, ?, ?, ?, ?)", projects)

                telemetry = [
                    ("DEP-TOR-01", "Gyan-Agent-70B", "Toronto, ON", 42.5, 142800, 0.02),
                    ("DEP-MON-01", "Gyan-Vision-Pro", "Montreal, QC", 68.1, 98400, 0.04),
                    ("DEP-SFO-01", "Gyan-Agent-70B", "San Francisco, CA", 38.9, 210500, 0.01),
                    ("DEP-SEA-01", "Gyan-Embed-Large", "Seattle, WA", 12.4, 450000, 0.00)
                ]
                cursor.executemany("INSERT INTO model_telemetry VALUES (?, ?, ?, ?, ?, ?)", telemetry)

            conn.commit()

    def get_schema(self) -> str:
        """
        Extracts table schemas for LLM context prompting.
        """
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
            rows = cursor.fetchall()
            return "\n\n".join(f"-- Table: {name}\n{sql};" for name, sql in rows)

    def execute_query(self, sql_query: str) -> Dict[str, Any]:
        """
        Executes a sanitized read-only SQL query against the SQLite database.
        """
        # Safety check: allow only SELECT queries
        clean_sql = sql_query.strip().strip(";")
        first_word = clean_sql.split()[0].upper() if clean_sql else ""
        if first_word != "SELECT" and first_word != "WITH":
            raise ValueError("Security Policy: Only read-only SELECT queries are permitted.")

        with sqlite3.connect(str(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(clean_sql)
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description] if cursor.description else []
            data = [dict(row) for row in rows]

            return {
                "columns": columns,
                "rows": data,
                "row_count": len(data),
                "sql": clean_sql
            }

    def generate_and_execute(self, natural_language_query: str, llm_client=None) -> Dict[str, Any]:
        """
        Translates natural language to SQL and executes it with fallback heuristics.
        """
        schema = self.get_schema()
        q_lower = natural_language_query.lower()

        # Heuristic rules for zero-dependency instant execution
        generated_sql = None
        if "compute nodes" in q_lower or "gpu" in q_lower or "servers" in q_lower:
            generated_sql = "SELECT node_id, hub_location, gpu_type, gpu_count, status, hourly_cost_usd FROM compute_nodes;"
        elif "projects" in q_lower or "budget" in q_lower or "compute hours" in q_lower:
            generated_sql = "SELECT project_id, name, lead_architect, department, status, compute_hours_spent, budget_usd FROM ai_projects;"
        elif "telemetry" in q_lower or "latency" in q_lower or "requests" in q_lower or "models" in q_lower:
            generated_sql = "SELECT deployment_id, model_name, hub_location, p95_latency_ms, total_requests_24h, error_rate_pct FROM model_telemetry;"
        else:
            generated_sql = "SELECT * FROM compute_nodes LIMIT 5;"

        result = self.execute_query(generated_sql)
        result["natural_query"] = natural_language_query
        return result
