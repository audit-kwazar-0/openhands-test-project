#!/usr/bin/env python3
"""CLI for Lab Sentinel (invoke via ./labctl wrapper → .venv)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from lab_sentinel.config import Config
from lab_sentinel.db import bootstrap_from_config, latest_results, list_services
from lab_sentinel.poller import HealthPoller


def cmd_init(config_path: Path) -> int:
    cfg = Config.load(config_path)
    bootstrap_from_config(cfg)
    print(f"initialized {cfg.db_path}")
    return 0


def cmd_status(config_path: Path) -> int:
    cfg = Config.load(config_path)
    bootstrap_from_config(cfg)
    services = [dict(r) for r in list_services(cfg.db_path)]
    checks = [dict(r) for r in latest_results(cfg.db_path, limit=20)]
    print(json.dumps({"services": services, "recent_checks": checks}, indent=2))
    return 0


def cmd_check(config_path: Path) -> int:
    cfg = Config.load(config_path)
    bootstrap_from_config(cfg)
    n = HealthPoller(cfg.db_path).run_once()
    print(f"ran {n} check(s)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="labctl")
    parser.add_argument("-c", "--config", type=Path, default=Path("config/lab.yaml"))
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init", help="create DB and sync services from YAML")
    sub.add_parser("status", help="print services and recent checks as JSON")
    sub.add_parser("check", help="run due health checks once")
    args = parser.parse_args()

    handlers = {
        "init": cmd_init,
        "status": cmd_status,
        "check": cmd_check,
    }
    return handlers[args.command](args.config)


if __name__ == "__main__":
    sys.exit(main())
