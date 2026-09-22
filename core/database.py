"""SQLite persistence for users, experiments, lab readings, and timeseries."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

DB_PATH = Path(__file__).resolve().parents[1] / "anammox.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def create_tables() -> None:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token TEXT UNIQUE NOT NULL
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS experiments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            created_at TEXT,
            stage TEXT DEFAULT 'anammox',
            nh4 REAL,
            no2 REAL,
            no3 REAL,
            hco3 REAL DEFAULT 0,
            ph REAL,
            temperature REAL,
            do REAL,
            biomass REAL,
            srt REAL,
            final_nh4 REAL,
            final_no2 REAL,
            final_no3 REAL,
            final_biomass REAL,
            stability REAL,
            initial_no3 REAL DEFAULT 0,
            notes TEXT DEFAULT '',
            lab_table_json TEXT DEFAULT '',
            sim_sources_json TEXT DEFAULT ''
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS experiment_timeseries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            experiment_id INTEGER,
            day INTEGER,
            nh4 REAL,
            no2 REAL,
            no3 REAL,
            biomass REAL,
            stability REAL
        )
        """
    )

    conn.commit()
    conn.close()

    create_lab_tables()
    migrate_experiments_table()


def create_lab_tables() -> None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS lab_readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            created_at TEXT,
            stage TEXT,
            nh4 REAL,
            no2 REAL,
            no3 REAL,
            ph REAL,
            temperature REAL,
            do REAL,
            srt REAL,
            hco3 REAL,
            notes TEXT,
            status TEXT,
            findings TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def migrate_experiments_table() -> None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(experiments)")
    columns = {row[1] for row in cursor.fetchall()}

    migrations = {
        "stage": "ALTER TABLE experiments ADD COLUMN stage TEXT DEFAULT 'anammox'",
        "initial_no3": "ALTER TABLE experiments ADD COLUMN initial_no3 REAL DEFAULT 0",
        "hco3": "ALTER TABLE experiments ADD COLUMN hco3 REAL DEFAULT 120",
        "notes": "ALTER TABLE experiments ADD COLUMN notes TEXT DEFAULT ''",
        "lab_table_json": "ALTER TABLE experiments ADD COLUMN lab_table_json TEXT DEFAULT ''",
        "sim_sources_json": "ALTER TABLE experiments ADD COLUMN sim_sources_json TEXT DEFAULT ''",
    }
    for col, sql in migrations.items():
        if col not in columns:
            cursor.execute(sql)

    conn.commit()
    conn.close()


def save_experiment(
    config,
    final_nh4: float = 0.0,
    final_no2: float = 0.0,
    final_no3: float = 0.0,
    final_biomass: float = 0.0,
    stability: float = 0.0,
    user_id: int | None = None,
    stage: str = "anammox",
    initial_no3: float = 0.0,
    notes: str = "",
    lab_table_json: str = "",
    sim_sources_json: str = "",
) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO experiments (
            user_id, created_at, stage, nh4, no2, no3, hco3, ph, temperature, do,
            biomass, srt, final_nh4, final_no2, final_no3, final_biomass, stability,
            initial_no3, notes, lab_table_json, sim_sources_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            _now_iso(),
            stage,
            float(getattr(config, "nh4", 0.0)),
            float(getattr(config, "no2", 0.0)),
            float(getattr(config, "no3", 0.0)),
            float(getattr(config, "hco3", 0.0)),
            float(getattr(config, "ph", 7.8)),
            float(getattr(config, "temperature", 35.0)),
            float(getattr(config, "do", 0.8)),
            float(getattr(config, "x_anammox", getattr(config, "x_aob", 0.0))),
            float(getattr(config, "srt", 20.0)),
            float(final_nh4),
            float(final_no2),
            float(final_no3),
            float(final_biomass),
            float(stability),
            float(initial_no3),
            notes or "",
            lab_table_json or "",
            sim_sources_json or "",
        ),
    )
    experiment_id = int(cursor.lastrowid)
    conn.commit()
    conn.close()
    return experiment_id


def save_lab_reading(
    *,
    user_id: int,
    stage: str,
    nh4: float,
    no2: float,
    no3: float,
    ph: float,
    temperature: float,
    do: float,
    srt: float,
    notes: str = "",
    status: str = "",
    findings: str = "",
    hco3: float | None = None,
) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO lab_readings (
            user_id, created_at, stage, nh4, no2, no3, ph, temperature, do, srt,
            hco3, notes, status, findings
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            _now_iso(),
            stage,
            float(nh4),
            float(no2),
            float(no3),
            float(ph),
            float(temperature),
            float(do),
            float(srt),
            float(hco3 or 0.0),
            notes or "",
            status or "",
            findings or "",
        ),
    )
    reading_id = int(cursor.lastrowid)
    conn.commit()
    conn.close()
    return reading_id


def save_timeseries(experiment_id: int, df: pd.DataFrame) -> None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM experiment_timeseries WHERE experiment_id = ?",
        (experiment_id,),
    )

    day_col = "Day" if "Day" in df.columns else "day"
    nh4_col = "NH4" if "NH4" in df.columns else "nh4"
    no2_col = "NO2" if "NO2" in df.columns else "no2"
    no3_col = "NO3" if "NO3" in df.columns else "no3"
    biomass_col = next((c for c in ("Biomass", "AOB", "biomass") if c in df.columns), None)
    stability_col = next((c for c in ("Stability", "NAR", "stability") if c in df.columns), None)

    for _, row in df.iterrows():
        cursor.execute(
            """
            INSERT INTO experiment_timeseries (
                experiment_id, day, nh4, no2, no3, biomass, stability
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                experiment_id,
                int(row[day_col]),
                float(row[nh4_col]),
                float(row[no2_col]),
                float(row[no3_col]),
                float(row[biomass_col]) if biomass_col else 0.0,
                float(row[stability_col]) if stability_col else 0.0,
            ),
        )

    conn.commit()
    conn.close()


def _rows_to_df(rows) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame([dict(row) for row in rows])


def get_experiments(user_id: int | None = None) -> pd.DataFrame:
    conn = get_connection()
    cursor = conn.cursor()
    if user_id is None:
        cursor.execute("SELECT * FROM experiments ORDER BY id DESC")
    else:
        cursor.execute(
            "SELECT * FROM experiments WHERE user_id = ? ORDER BY id DESC",
            (user_id,),
        )
    rows = cursor.fetchall()
    conn.close()
    return _rows_to_df(rows)


def get_user_experiments(user_id: int) -> pd.DataFrame:
    return get_experiments(user_id=user_id)


def get_all_experiment_ids(user_id: int | None = None) -> list[int]:
    df = get_experiments(user_id=user_id)
    if df.empty:
        return []
    return [int(x) for x in df["id"].tolist()]


def get_experiment_by_id(experiment_id: int) -> pd.DataFrame:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM experiments WHERE id = ?", (experiment_id,))
    rows = cursor.fetchall()
    conn.close()
    return _rows_to_df(rows)


def get_experiment_timeseries(experiment_id: int) -> pd.DataFrame:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT day, nh4, no2, no3, biomass, stability
        FROM experiment_timeseries
        WHERE experiment_id = ?
        ORDER BY day
        """,
        (experiment_id,),
    )
    rows = cursor.fetchall()
    conn.close()
    return _rows_to_df(rows)


def get_lab_readings(user_id: int, limit: int = 10) -> pd.DataFrame:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT * FROM lab_readings
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT ?
        """,
        (user_id, limit),
    )
    rows = cursor.fetchall()
    conn.close()
    return _rows_to_df(rows)


def get_username_by_id(user_id: int) -> str | None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return str(row[0]) if row else None


def get_all_users() -> pd.DataFrame:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, is_admin FROM users ORDER BY id")
    rows = cursor.fetchall()
    conn.close()
    return _rows_to_df(rows)


def delete_user(user_id: int) -> None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()


def delete_experiment(experiment_id: int) -> None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM experiment_timeseries WHERE experiment_id = ?", (experiment_id,))
    cursor.execute("DELETE FROM experiments WHERE id = ?", (experiment_id,))
    conn.commit()
    conn.close()


def get_dashboard_stats() -> dict[str, int]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    users = int(cursor.fetchone()[0])
    cursor.execute("SELECT COUNT(*) FROM experiments")
    experiments = int(cursor.fetchone()[0])
    cursor.execute("SELECT COUNT(*) FROM lab_readings")
    readings = int(cursor.fetchone()[0])
    conn.close()
    return {
        "users": users,
        "experiments": experiments,
        "lab_readings": readings,
    }
