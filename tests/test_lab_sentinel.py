from __future__ import annotations

from pathlib import Path

import yaml
from fastapi.testclient import TestClient

from lab_sentinel.api import create_app
from lab_sentinel.config import Config, ServiceConfig
from lab_sentinel.db import bootstrap_from_config, list_services, record_check, sync_services
from lab_sentinel.poller import check_url


def test_config_load(tmp_path: Path) -> None:
    cfg_file = tmp_path / "lab.yaml"
    cfg_file.write_text(
        yaml.dump(
            {
                "db_path": str(tmp_path / "test.db"),
                "services": [
                    {"name": "x", "url": "http://example.com", "interval_sec": 10}
                ],
            }
        ),
        encoding="utf-8",
    )
    cfg = Config.load(cfg_file)
    assert cfg.db_path == tmp_path / "test.db"
    assert len(cfg.services) == 1


def test_db_and_api(tmp_path: Path) -> None:
    db = tmp_path / "lab.db"
    cfg = Config(db_path=db, services=[])
    bootstrap_from_config(cfg)
    sync_services(db, [ServiceConfig(name="a", url="http://a", interval_sec=5)])
    rows = list_services(db)
    sid = int(rows[0]["id"])
    record_check(db, sid, "up", 0.05)

    client = TestClient(create_app(db))
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/services").json()[0]["name"] == "a"
    assert client.get("/checks").json()[0]["status"] == "up"


def test_check_url_invalid() -> None:
    status, elapsed = check_url("http://127.0.0.1:1", timeout=0.5)
    assert status == "down"
    assert elapsed is None
