from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable, List, Optional

from lab_sentinel.config import Config, ServiceConfig


def _connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Path) -> None:
    with _connect(db_path) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                url TEXT NOT NULL,
                interval_sec INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS check_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_id INTEGER NOT NULL,
                timestamp TEXT NOT NULL,
                status TEXT NOT NULL,
                response_time REAL,
                FOREIGN KEY(service_id) REFERENCES services(id)
            );
            """
        )
        conn.commit()


def sync_services(db_path: Path, services: Iterable[ServiceConfig]) -> None:
    with _connect(db_path) as conn:
        for svc in services:
            conn.execute(
                """
                INSERT INTO services (name, url, interval_sec)
                VALUES (?, ?, ?)
                ON CONFLICT(name) DO UPDATE SET
                    url = excluded.url,
                    interval_sec = excluded.interval_sec
                """,
                (svc.name, svc.url, svc.interval_sec),
            )
        conn.commit()


def list_services(db_path: Path) -> List[sqlite3.Row]:
    with _connect(db_path) as conn:
        return list(conn.execute("SELECT * FROM services ORDER BY name"))


def record_check(
    db_path: Path,
    service_id: int,
    status: str,
    response_time: Optional[float],
) -> None:
    from datetime import datetime, timezone

    ts = datetime.now(timezone.utc).isoformat()
    with _connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO check_results (service_id, timestamp, status, response_time)
            VALUES (?, ?, ?, ?)
            """,
            (service_id, ts, status, response_time),
        )
        conn.commit()


def latest_results(db_path: Path, limit: int = 50) -> List[sqlite3.Row]:
    with _connect(db_path) as conn:
        return list(
            conn.execute(
                """
                SELECT cr.*, s.name AS service_name
                FROM check_results cr
                JOIN services s ON s.id = cr.service_id
                ORDER BY cr.id DESC
                LIMIT ?
                """,
                (limit,),
            )
        )


def bootstrap_from_config(config: Config) -> None:
    init_db(config.db_path)
    sync_services(config.db_path, config.services)
