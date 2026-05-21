from __future__ import annotations

import argparse
import logging
import threading
from pathlib import Path

import uvicorn

from lab_sentinel.api import create_app
from lab_sentinel.config import Config
from lab_sentinel.db import bootstrap_from_config
from lab_sentinel.poller import HealthPoller

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("lab_sentinel")


def main() -> None:
    parser = argparse.ArgumentParser(description="Lab Sentinel monitor")
    parser.add_argument(
        "-c",
        "--config",
        type=Path,
        default=Path("config/lab.yaml"),
        help="Path to lab.yaml",
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--no-poller", action="store_true")
    args = parser.parse_args()

    config = Config.load(args.config)
    bootstrap_from_config(config)
    logger.info("database: %s", config.db_path.resolve())

    if not args.no_poller:
        poller = HealthPoller(config.db_path)

        def _run_poller() -> None:
            poller.loop()

        thread = threading.Thread(target=_run_poller, daemon=True)
        thread.start()

    app = create_app(config.db_path)
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")


if __name__ == "__main__":
    main()
