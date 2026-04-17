from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from morgantown_ops_hub.config_loader import (
    ConfigValidationError,
    load_config_bundle,
    load_source_manifest,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def _base_sources_manifest() -> dict:
    return {
        "site": "Morgantown",
        "plant_scope": "North Plant",
        "sources": [
            {
                "source_id": "liquids_schedule",
                "source_name": "Liquids Schedule",
                "source_type": "sharepoint_workbook",
                "site_scope": "Morgantown",
                "plant_scope": "North Plant",
                "domain": "planned_schedule",
                "path": "Schedules/Liquids.xlsm",
                "selection_rules": {"latest_only": True},
                "enabled": True,
                "authoritative_for": ["planned_schedule"],
                "expected_refresh": "daily",
                "timestamp_strategy": "business_timestamp",
            }
        ],
        "exclusions": {
            "sharepoint_paths": ["Morgantown/Operations/South Plant"],
            "filename_contains": ["Archive", "South Plant"],
            "notes": [],
        },
    }


def _valid_precedence() -> dict:
    return {
        "precedence": {
            "planned_schedule": {
                "preferred_sources": ["liquids_schedule"],
                "notes": [],
            }
        }
    }


def _valid_refresh() -> dict:
    return {
        "rules": [
            {
                "source_id": "liquids_schedule",
                "metric": "source_age_minutes",
                "warning_threshold": 60,
                "error_threshold": 120,
            }
        ]
    }


def _write_config_file(path: Path, payload: dict) -> None:
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")


def test_source_manifest_loads_successfully() -> None:
    manifest = load_source_manifest(REPO_ROOT / "config" / "sources.yaml")

    assert manifest.site == "Morgantown"
    assert manifest.plant_scope == "North Plant"
    assert len(manifest.sources) == 9


def test_duplicate_source_id_fails(tmp_path: Path) -> None:
    manifest_payload = _base_sources_manifest()
    manifest_payload["sources"].append({**manifest_payload["sources"][0], "source_name": "Duplicate Liquids"})
    manifest_path = tmp_path / "sources.yaml"
    _write_config_file(manifest_path, manifest_payload)

    with pytest.raises(ConfigValidationError, match="Duplicate source_id"):
        load_source_manifest(manifest_path)


def test_unknown_source_in_precedence_fails(tmp_path: Path) -> None:
    _write_config_file(tmp_path / "sources.yaml", _base_sources_manifest())
    precedence_payload = _valid_precedence()
    precedence_payload["precedence"]["planned_schedule"]["preferred_sources"].append("unknown_source")
    _write_config_file(tmp_path / "precedence_rules.yaml", precedence_payload)
    _write_config_file(tmp_path / "refresh_rules.yaml", _valid_refresh())

    with pytest.raises(ConfigValidationError, match="precedence rules reference unknown source_id"):
        load_config_bundle(tmp_path)


def test_unknown_source_in_refresh_rules_fails(tmp_path: Path) -> None:
    _write_config_file(tmp_path / "sources.yaml", _base_sources_manifest())
    _write_config_file(tmp_path / "precedence_rules.yaml", _valid_precedence())
    refresh_payload = _valid_refresh()
    refresh_payload["rules"][0]["source_id"] = "unknown_source"
    _write_config_file(tmp_path / "refresh_rules.yaml", refresh_payload)

    with pytest.raises(ConfigValidationError, match="refresh rules reference unknown source_id"):
        load_config_bundle(tmp_path)
