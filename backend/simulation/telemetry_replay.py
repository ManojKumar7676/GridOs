"""Normalize imported field telemetry and replay measurements through the local optimizer."""

import re
import os
import sqlite3
from typing import Any, Dict, Iterable, List, Optional
from datetime import datetime, timezone
from contextlib import closing

import numpy as np
import pandas as pd

from AccentureAssessment.backend.core.portfolio import AssetStatus, UtilityPortfolioState
from AccentureAssessment.backend.core.solver import DispatchWeights, IndustrialDispatchSolver


FIELD_ALIASES = {
    "timestamp": {"timestamp", "time", "datetime", "recorded_at", "device_timestamp", "ts"},
    "solar_generation_mw": {"solar_generation_mw", "solar_gen_mw", "solar_mw", "pv_generation_mw", "pv_mw"},
    "wind_generation_mw": {"wind_generation_mw", "wind_gen_mw", "wind_mw"},
    "demand_mw": {"demand_mw", "demand", "load_mw", "served_demand_mw", "served_load_mw", "industrial_load_mw"},
    "spot_price_usd_mwh": {"spot_price_usd_mwh", "spot_price", "lmp_usd_mwh", "lmp", "market_price_usd_mwh"},
    "bess1_soc_pct": {"bess1_soc_pct", "bess_1_soc_pct", "battery1_soc_pct"},
    "bess2_soc_pct": {"bess2_soc_pct", "bess_2_soc_pct", "battery2_soc_pct"},
    "wind_speed_mps": {"wind_speed_mps", "wind_speed", "wind_mps"},
    "cloud_index": {"cloud_index", "cloud_density", "cloud_opacity_index", "cloud_density_pct", "cloud_opacity_pct"},
    "grid_frequency_hz": {"grid_frequency_hz", "frequency_hz", "frequency"},
    "voltage_kv": {"voltage_kv", "grid_voltage_kv", "voltage"},
    "transmission_congested": {"transmission_congested", "grid_congested", "congestion"},
    "bess1_available": {"bess1_available", "bess_1_available", "battery1_available"},
}

REQUIRED_FIELDS = ("solar_generation_mw", "wind_generation_mw", "demand_mw", "spot_price_usd_mwh")
OPTIONAL_NUMERIC_FIELDS = (
    "bess1_soc_pct", "bess2_soc_pct", "wind_speed_mps", "cloud_index", "grid_frequency_hz", "voltage_kv"
)
OPTIONAL_BOOLEAN_FIELDS = ("transmission_congested", "bess1_available")


class HardwareTelemetryStore:
    """Small compatibility-safe repository for imported readings in the app database."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        parent = os.path.dirname(db_path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with closing(sqlite3.connect(self.db_path)) as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS hardware_telemetry_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    imported_at TEXT NOT NULL,
                    source_file TEXT NOT NULL,
                    device_timestamp TEXT NOT NULL,
                    solar_generation_mw REAL NOT NULL,
                    wind_generation_mw REAL NOT NULL,
                    demand_mw REAL NOT NULL,
                    spot_price_usd_mwh REAL NOT NULL,
                    bess1_soc_pct REAL, bess2_soc_pct REAL, wind_speed_mps REAL,
                    cloud_index REAL, grid_frequency_hz REAL, voltage_kv REAL,
                    transmission_congested INTEGER, bess1_available INTEGER
                )
            """)

    def save(self, records: List[Dict[str, Any]], source_file: str) -> int:
        if not records:
            return 0
        imported_at = datetime.now(timezone.utc).isoformat()
        fields = (
            "bess1_soc_pct", "bess2_soc_pct", "wind_speed_mps", "cloud_index",
            "grid_frequency_hz", "voltage_kv", "transmission_congested", "bess1_available",
        )
        rows = []
        for record in records:
            optional = [record.get(field) for field in fields]
            optional = [
                None if value is None or (isinstance(value, (float, np.floating)) and not np.isfinite(value))
                else value.item() if isinstance(value, np.generic) else value
                for value in optional
            ]
            rows.append((
                imported_at, os.path.basename(source_file) or "hardware-telemetry-upload", str(record["timestamp"]),
                float(record["solar_generation_mw"]), float(record["wind_generation_mw"]),
                float(record["demand_mw"]), float(record["spot_price_usd_mwh"]), *optional,
            ))
        with closing(sqlite3.connect(self.db_path)) as connection:
            with connection:
                connection.executemany("""
                    INSERT INTO hardware_telemetry_records (
                        imported_at, source_file, device_timestamp, solar_generation_mw,
                        wind_generation_mw, demand_mw, spot_price_usd_mwh, bess1_soc_pct,
                        bess2_soc_pct, wind_speed_mps, cloud_index, grid_frequency_hz,
                        voltage_kv, transmission_congested, bess1_available
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, rows)
        return len(rows)

    def get_recent(self, limit: int = 5000) -> List[Dict[str, Any]]:
        limit = max(1, min(int(limit), 5000))
        with closing(sqlite3.connect(self.db_path)) as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(
                "SELECT * FROM hardware_telemetry_records ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
        return [dict(row) for row in reversed(rows)]


def _canonical_column(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(value).strip().casefold()).strip("_")


def _parse_optional_bool(value: Any, field: str, row_number: int) -> Optional[bool]:
    if pd.isna(value) or str(value).strip() == "":
        return None
    if isinstance(value, (bool, np.bool_)):
        return bool(value)
    normalized = str(value).strip().casefold()
    if normalized in {"1", "true", "yes", "y", "on", "connected", "available"}:
        return True
    if normalized in {"0", "false", "no", "n", "off", "disconnected", "unavailable"}:
        return False
    raise ValueError(f"Row {row_number}: {field} must be true/false, yes/no, or 1/0.")


def normalize_hardware_telemetry(frame: pd.DataFrame) -> pd.DataFrame:
    """Normalize CSV/JSON telemetry headers and validate values used in replay."""
    if frame.empty:
        raise ValueError("The telemetry file has no records.")
    if len(frame) > 5000:
        raise ValueError("Import is limited to 5,000 records per file.")

    aliases = {alias: field for field, names in FIELD_ALIASES.items() for alias in names}
    renamed: Dict[str, str] = {}
    for column in frame.columns:
        canonical = _canonical_column(column)
        renamed[column] = aliases.get(canonical, canonical)
    normalized = frame.rename(columns=renamed).copy()
    if normalized.columns.duplicated().any():
        raise ValueError("The file contains multiple columns that map to the same telemetry field.")

    missing = [field for field in REQUIRED_FIELDS if field not in normalized.columns]
    if missing:
        raise ValueError("Missing required fields: " + ", ".join(missing) + ". Required: solar generation, wind generation, demand, and spot price.")

    result = pd.DataFrame(index=normalized.index)
    if "timestamp" in normalized.columns:
        result["timestamp"] = normalized["timestamp"].fillna("").astype(str).str.strip()
    else:
        result["timestamp"] = ""

    limits = {
        "solar_generation_mw": (0.0, 230.0),
        "wind_generation_mw": (0.0, 250.0),
        "demand_mw": (0.0, 10000.0),
        "spot_price_usd_mwh": (-1000.0, 10000.0),
        "bess1_soc_pct": (0.0, 100.0),
        "bess2_soc_pct": (0.0, 100.0),
        "wind_speed_mps": (0.0, 100.0),
        "cloud_index": (0.0, 1.0),
        "grid_frequency_hz": (0.0, 100.0),
        "voltage_kv": (0.0, 2000.0),
    }
    for field in REQUIRED_FIELDS:
        values = pd.to_numeric(normalized[field], errors="coerce")
        invalid = values.isna() | ~np.isfinite(values)
        if invalid.any():
            row_number = int(np.flatnonzero(invalid.to_numpy())[0]) + 2
            raise ValueError(f"Row {row_number}: {field} must be a finite number.")
        lower, upper = limits[field]
        outside = (values < lower) | (values > upper)
        if outside.any():
            row_number = int(np.flatnonzero(outside.to_numpy())[0]) + 2
            raise ValueError(f"Row {row_number}: {field} must be between {lower:g} and {upper:g}.")
        result[field] = values.astype(float)

    for field in OPTIONAL_NUMERIC_FIELDS:
        if field not in normalized.columns:
            result[field] = np.nan
            continue
        values = pd.to_numeric(normalized[field].replace(r"^\s*$", np.nan, regex=True), errors="coerce")
        invalid_text = normalized[field].notna() & normalized[field].astype(str).str.strip().ne("") & values.isna()
        if invalid_text.any():
            row_number = int(np.flatnonzero(invalid_text.to_numpy())[0]) + 2
            raise ValueError(f"Row {row_number}: {field} must be numeric when supplied.")
        if field == "cloud_index" and values.notna().any() and values.max() > 1.0:
            values = values / 100.0
        lower, upper = limits[field]
        outside = values.notna() & ((values < lower) | (values > upper))
        if outside.any():
            row_number = int(np.flatnonzero(outside.to_numpy())[0]) + 2
            raise ValueError(f"Row {row_number}: {field} must be between {lower:g} and {upper:g}.")
        result[field] = values.astype(float)

    for field in OPTIONAL_BOOLEAN_FIELDS:
        if field not in normalized.columns:
            result[field] = None
        else:
            result[field] = [
                _parse_optional_bool(value, field, index + 2)
                for index, value in enumerate(normalized[field].tolist())
            ]

    result["timestamp"] = [value if value else f"Interval {i + 1:02d}" for i, value in enumerate(result["timestamp"].tolist())]
    return result.reset_index(drop=True)


def replay_hardware_telemetry(
    records: Iterable[Dict[str, Any]],
    solver: Optional[IndustrialDispatchSolver] = None,
) -> pd.DataFrame:
    """Replay measured renewable output, demand and market prices through SCED."""
    rows = list(records)
    if not rows:
        return pd.DataFrame()
    solver = solver or IndustrialDispatchSolver()
    portfolio = UtilityPortfolioState()
    output: List[Dict[str, Any]] = []

    for index, row in enumerate(rows):
        portfolio.market.spot_price_per_mwh = float(row["spot_price_usd_mwh"])
        next_price = rows[min(index + 4, len(rows) - 1)]["spot_price_usd_mwh"]
        portfolio.market.projected_price_next_hour = float(next_price)
        portfolio.grid.transmission_congested = bool(row.get("transmission_congested")) if row.get("transmission_congested") is not None else False

        if index == 0:
            for battery_index, key in enumerate(("bess1_soc_pct", "bess2_soc_pct")):
                measured_soc = row.get(key)
                if measured_soc is not None and pd.notna(measured_soc):
                    portfolio.bess_systems[battery_index].current_soc_pct = float(measured_soc)
        if row.get("bess1_available") is not None:
            portfolio.bess_systems[0].is_available = bool(row["bess1_available"])
            portfolio.bess_systems[0].status = AssetStatus.OPERATIONAL if row["bess1_available"] else AssetStatus.MAINTENANCE

        # Replay the measured site demand as fixed demand; the prototype does not
        # infer or invent industrial flexibility from a meter reading.
        portfolio.industrial_consumers[0].base_load_mw = float(row["demand_mw"])
        portfolio.industrial_consumers[0].flexible_shiftable_mw = 0.0
        portfolio.industrial_consumers[0].interruptible_mw = 0.0
        for consumer in portfolio.industrial_consumers[1:]:
            consumer.base_load_mw = 0.0
            consumer.flexible_shiftable_mw = 0.0
            consumer.interruptible_mw = 0.0

        wind_speed = row.get("wind_speed_mps")
        if wind_speed is not None and pd.notna(wind_speed):
            for farm in portfolio.wind_farms:
                farm.wind_speed_mps = float(wind_speed)

        result = solver.solve(
            portfolio,
            DispatchWeights(),
            solar_generation_override_mw=float(row["solar_generation_mw"]),
            wind_generation_override_mw=float(row["wind_generation_mw"]),
        )
        frequency = row.get("grid_frequency_hz")
        frequency_status = "Not provided" if frequency is None or pd.isna(frequency) else (
            "Review" if float(frequency) < 49.85 or float(frequency) > 50.15 else "Within configured band"
        )
        supply = result.solar_generation_mw + result.wind_generation_mw + result.bess1_discharge_mw + result.bess2_discharge_mw + result.grid_import_mw
        disposition = result.served_demand_mw + result.bess1_charge_mw + result.bess2_charge_mw + result.grid_export_mw
        output.append({
            "timestamp": row.get("timestamp", f"Interval {index + 1:02d}"),
            "measured_solar_mw": float(row["solar_generation_mw"]),
            "measured_wind_mw": float(row["wind_generation_mw"]),
            "measured_demand_mw": float(row["demand_mw"]),
            "spot_price_usd_mwh": float(row["spot_price_usd_mwh"]),
            "measured_bess1_soc_pct": row.get("bess1_soc_pct"),
            "measured_bess2_soc_pct": row.get("bess2_soc_pct"),
            "dispatch_solar_mw": result.solar_generation_mw,
            "dispatch_wind_mw": result.wind_generation_mw,
            "served_demand_mw": result.served_demand_mw,
            "bess1_soc_pct": result.bess1_next_soc_pct,
            "bess2_soc_pct": result.bess2_next_soc_pct,
            "grid_import_mw": result.grid_import_mw,
            "grid_export_mw": result.grid_export_mw,
            "unserved_demand_mw": result.unserved_demand_mw,
            "net_value_usd": result.market_revenue_cost_usd,
            "frequency_hz": frequency,
            "frequency_status": frequency_status,
            "solver_status": result.solver_status,
            "power_balance_residual_mw": round(supply - disposition, 4),
        })
        portfolio.bess_systems[0].current_soc_pct = result.bess1_next_soc_pct
        portfolio.bess_systems[1].current_soc_pct = result.bess2_next_soc_pct

    return pd.DataFrame(output)
