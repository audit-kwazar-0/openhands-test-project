from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Dict
from urllib.error import URLError
from urllib.request import Request, urlopen

from lab_sentinel.db import list_services, record_check

logger = logging.getLogger(__name__)


def check_url(url: str, timeout: float = 5.0) -> tuple[str, float | None]:
    started = time.perf_counter()
    try:
        req = Request(url, method="GET", headers={"User-Agent": "LabSentinel/0.1"})
        with urlopen(req, timeout=timeout) as resp:
            elapsed = time.perf_counter() - started
            if 200 <= resp.status < 400:
                return "up", elapsed
            return "down", elapsed
    except (URLError, TimeoutError, OSError) as exc:
        logger.debug("check failed for %s: %s", url, exc)
        return "down", None


class HealthPoller:
    def __init__(self, db_path: Path, default_interval: int = 60) -> None:
        self.db_path = db_path
        self.default_interval = default_interval
        self._last_run: Dict[int, float] = {}

    def run_once(self) -> int:
        now = time.time()
        checked = 0
        for row in list_services(self.db_path):
            sid = int(row["id"])
            interval = int(row["interval_sec"] or self.default_interval)
            last = self._last_run.get(sid, 0.0)
            if now - last < interval:
                continue
            status, elapsed = check_url(str(row["url"]))
            record_check(self.db_path, sid, status, elapsed)
            self._last_run[sid] = now
            checked += 1
        return checked

    def loop(self, tick_sec: float = 5.0) -> None:
        logger.info("poller started (tick=%ss)", tick_sec)
        while True:
            n = self.run_once()
            if n:
                logger.info("checked %s service(s)", n)
            time.sleep(tick_sec)
