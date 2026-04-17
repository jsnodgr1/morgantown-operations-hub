"""Source configuration loading and extraction entry points."""

from __future__ import annotations

from pathlib import Path

import yaml

from morgantown_ops_hub.models import SourceConfig


def load_source_configs(config_path: Path) -> list[SourceConfig]:
    """Load source definitions from a YAML file."""
    payload = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    raw_sources = payload.get("sources", [])
    return [SourceConfig(**item) for item in raw_sources]


def get_enabled_sources(configs: list[SourceConfig]) -> list[SourceConfig]:
    """Return only the sources marked as enabled."""
    return [config for config in configs if config.enabled]
