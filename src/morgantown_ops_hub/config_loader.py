"""Load and cross-validate YAML configuration for the V1 scaffold."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from morgantown_ops_hub.config_models import (
    PrecedenceRules,
    RefreshRules,
    SourceManifest,
)


class ConfigValidationError(ValueError):
    """Raised when config files are invalid or inconsistent."""


class ConfigBundle:
    """Container for the validated configuration set."""

    def __init__(
        self,
        manifest: SourceManifest,
        precedence_rules: PrecedenceRules,
        refresh_rules: RefreshRules,
        config_dir: Path,
    ) -> None:
        self.manifest = manifest
        self.precedence_rules = precedence_rules
        self.refresh_rules = refresh_rules
        self.config_dir = config_dir


def load_yaml_file(path: Path) -> dict[str, Any]:
    """Load a YAML mapping from disk."""
    try:
        with path.open("r", encoding="utf-8") as handle:
            payload = yaml.safe_load(handle)
    except FileNotFoundError as exc:
        raise ConfigValidationError(f"Config file not found: {path}") from exc
    except yaml.YAMLError as exc:
        raise ConfigValidationError(f"Invalid YAML in {path}: {exc}") from exc

    if not isinstance(payload, dict):
        raise ConfigValidationError(f"Expected a YAML mapping in {path}.")
    return payload


def _validate_model(model_cls: type[Any], payload: dict[str, Any], path: Path) -> Any:
    """Validate a YAML payload against a Pydantic model with a clear error wrapper."""
    try:
        return model_cls.model_validate(payload)
    except ValidationError as exc:
        raise ConfigValidationError(f"Invalid config in {path}: {exc}") from exc


def load_source_manifest(path: Path) -> SourceManifest:
    """Load and validate the source manifest."""
    return _validate_model(SourceManifest, load_yaml_file(path), path)


def load_precedence_rules(path: Path) -> PrecedenceRules:
    """Load and validate precedence rules."""
    return _validate_model(PrecedenceRules, load_yaml_file(path), path)


def load_refresh_rules(path: Path) -> RefreshRules:
    """Load and validate refresh rules."""
    return _validate_model(RefreshRules, load_yaml_file(path), path)


def validate_config_references(
    manifest: SourceManifest,
    precedence_rules: PrecedenceRules,
    refresh_rules: RefreshRules,
) -> None:
    """Validate cross-file references after each file passes schema validation."""
    known_source_ids = {source.source_id for source in manifest.sources}

    precedence_errors: list[str] = []
    for domain, rule in precedence_rules.precedence.items():
        unknown = [source_id for source_id in rule.preferred_sources if source_id not in known_source_ids]
        if unknown:
            joined = ", ".join(unknown)
            precedence_errors.append(f"{domain}: {joined}")

    refresh_unknown = [rule.source_id for rule in refresh_rules.rules if rule.source_id not in known_source_ids]

    messages: list[str] = []
    if precedence_errors:
        messages.append(
            "precedence rules reference unknown source_id values: "
            + "; ".join(precedence_errors)
        )
    if refresh_unknown:
        messages.append(
            "refresh rules reference unknown source_id values: "
            + ", ".join(sorted(set(refresh_unknown)))
        )
    if messages:
        raise ConfigValidationError("Config reference validation failed: " + " | ".join(messages))


def load_config_bundle(config_dir: Path) -> ConfigBundle:
    """Load all config files and validate them as one consistent bundle."""
    manifest = load_source_manifest(config_dir / "sources.yaml")
    precedence_rules = load_precedence_rules(config_dir / "precedence_rules.yaml")
    refresh_rules = load_refresh_rules(config_dir / "refresh_rules.yaml")
    validate_config_references(manifest, precedence_rules, refresh_rules)
    return ConfigBundle(
        manifest=manifest,
        precedence_rules=precedence_rules,
        refresh_rules=refresh_rules,
        config_dir=config_dir,
    )

