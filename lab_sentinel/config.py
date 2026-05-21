from __future__ import annotations

from pathlib import Path
from typing import List

import yaml
from pydantic import BaseModel, Field


class ServiceConfig(BaseModel):
    name: str
    url: str
    interval_sec: int = Field(ge=1, default=60)


class Config(BaseModel):
    db_path: Path = Path("data/lab_sentinel.db")
    services: List[ServiceConfig] = Field(default_factory=list)

    @classmethod
    def load(cls, path: Path) -> Config:
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        return cls.model_validate(raw)
