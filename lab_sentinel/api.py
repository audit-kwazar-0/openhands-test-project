from __future__ import annotations

from pathlib import Path
from typing import Any, List

from fastapi import FastAPI

from lab_sentinel.db import latest_results, list_services


def create_app(db_path: Path) -> FastAPI:
    app = FastAPI(title="Lab Sentinel", version="0.1.0")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/services")
    def services() -> List[dict[str, Any]]:
        return [dict(row) for row in list_services(db_path)]

    @app.get("/checks")
    def checks(limit: int = 50) -> List[dict[str, Any]]:
        return [dict(row) for row in latest_results(db_path, limit=limit)]

    return app
