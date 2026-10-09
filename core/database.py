"""
AccentureAssessment - Persistent SCADA & Dispatch Database
Production SQLite storage for telemetry records, executed action clusters, and multi-agent audit logs.
"""

import sqlite3
import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

class OrchestratorDatabase:
    """
    Manages ACID-compliant storage for industrial telemetry, dispatch runs,
    and agent decision audit trails.
    """

    DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "storage", "orchestrator.db")

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path if db_path is not None else self.DEFAULT_DB_PATH
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_schema()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. Telemetry & Energy Balance Records
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS telemetry_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    interval_idx INTEGER NOT NULL,
                    clock_time TEXT NOT NULL,
                    spot_price_usd_mwh REAL NOT NULL,
                    solar_generation_mw REAL NOT NULL,
                    wind_generation_mw REAL NOT NULL,
                    total_renewable_mw REAL NOT NULL,
                    served_demand_mw REAL NOT NULL,
                    bess1_soc_pct REAL NOT NULL,
                    bess2_soc_pct REAL NOT NULL,
                    bess_net_flow_mw REAL NOT NULL,
                    grid_export_mw REAL NOT NULL,
                    grid_import_mw REAL NOT NULL,
                    curtailed_mw REAL NOT NULL,
                    interval_net_financial_usd REAL NOT NULL,
                    carbon_avoided_kg REAL NOT NULL,
                    reserve_margin_mw REAL NOT NULL,
                    grid_stress_level TEXT NOT NULL,
                    optimality_score REAL NOT NULL,
                    event_tag TEXT
                )
            """)

            # 2. Executed Discrete Action Clusters (F1)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS executed_actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    interval_idx INTEGER NOT NULL,
                    timestamp TEXT NOT NULL,
                    category TEXT NOT NULL,
                    action_type TEXT NOT NULL,
                    target_asset TEXT NOT NULL,
                    amount_mw REAL NOT NULL,
                    rationale TEXT NOT NULL
                )
            """)

            # 3. Multi-Agent Audit Trail & Deliberation Logs (F2)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS agent_deliberations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    interval_idx INTEGER NOT NULL,
                    timestamp TEXT NOT NULL,
                    agent_name TEXT NOT NULL,
                    role TEXT NOT NULL,
                    observation TEXT NOT NULL,
                    reasoning TEXT NOT NULL,
                    recommendation_json TEXT NOT NULL
                )
            """)

            conn.commit()

    def log_dispatch_interval(
        self,
        interval_idx: int,
        clock_time: str,
        spot_price: float,
        solar_gen: float,
        wind_gen: float,
        served_demand: float,
        bess1_soc: float,
        bess2_soc: float,
        bess_net_flow: float,
        grid_export: float,
        grid_import: float,
        curtailed: float,
        net_financial: float,
        carbon_avoided: float,
        reserve_margin: float,
        grid_stress: str,
        optimality_score: float,
        event_tag: str,
        action_cluster: List[Dict[str, Any]],
        agent_logs: List[Dict[str, Any]]
    ):
        now_iso = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Insert Telemetry Record
            cursor.execute("""
                INSERT INTO telemetry_records (
                    timestamp, interval_idx, clock_time, spot_price_usd_mwh,
                    solar_generation_mw, wind_generation_mw, total_renewable_mw,
                    served_demand_mw, bess1_soc_pct, bess2_soc_pct, bess_net_flow_mw,
                    grid_export_mw, grid_import_mw, curtailed_mw, interval_net_financial_usd,
                    carbon_avoided_kg, reserve_margin_mw, grid_stress_level, optimality_score, event_tag
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                now_iso, interval_idx, clock_time, spot_price,
                solar_gen, wind_gen, solar_gen + wind_gen,
                served_demand, bess1_soc, bess2_soc, bess_net_flow,
                grid_export, grid_import, curtailed, net_financial,
                carbon_avoided, reserve_margin, grid_stress, optimality_score, event_tag
            ))

            # Insert Actions
            for act in action_cluster:
                cursor.execute("""
                    INSERT INTO executed_actions (
                        interval_idx, timestamp, category, action_type, target_asset, amount_mw, rationale
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    interval_idx, now_iso,
                    act.get("category", "SYSTEM"),
                    act.get("action", "DISPATCH"),
                    act.get("target", "PORTFOLIO"),
                    act.get("amount_mw", act.get("solar_mw", 0.0)),
                    act.get("rationale", "")
                ))

            # Insert Agent Logs
            for al in agent_logs:
                cursor.execute("""
                    INSERT INTO agent_deliberations (
                        interval_idx, timestamp, agent_name, role, observation, reasoning, recommendation_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    interval_idx, now_iso,
                    al.get("agent_name", "Agent"),
                    al.get("role", "Role"),
                    al.get("observation", ""),
                    al.get("reasoning", ""),
                    json.dumps(al.get("recommendation", {}))
                ))

            conn.commit()

    def get_recent_telemetry(self, limit: int = 96) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM telemetry_records ORDER BY id DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()
            return [dict(r) for r in reversed(rows)]

    def get_actions_for_interval(self, interval_idx: int) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM executed_actions WHERE interval_idx = ? ORDER BY id ASC", (interval_idx,))
            return [dict(r) for r in cursor.fetchall()]

    def get_agent_logs_for_interval(self, interval_idx: int) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM agent_deliberations WHERE interval_idx = ? ORDER BY id ASC", (interval_idx,))
            return [dict(r) for r in cursor.fetchall()]
