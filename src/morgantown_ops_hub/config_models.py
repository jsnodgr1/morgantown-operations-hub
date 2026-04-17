"""Typed configuration models for the V1 source manifest and rule files."""

from __future__ import annotations

import re
from enum import Enum
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class SourceType(str, Enum):
    """Supported source kinds for the local V1 scaffold."""

    SHAREPOINT_WORKBOOK = "sharepoint_workbook"
    SHAREPOINT_FOLDER = "sharepoint_folder"
    EMAIL = "email"


class RefreshMetric(str, Enum):
    """Supported freshness metrics."""

    SOURCE_AGE_MINUTES = "source_age_minutes"


class StrictBaseModel(BaseModel):
    """Base model that forbids undeclared fields in config payloads."""

    model_config = ConfigDict(extra="forbid")


class SelectionRules(StrictBaseModel):
    """Source-specific candidate selection rules."""

    latest_only: bool = False
    latest_n: int | None = None
    latest_per_day: bool = False
    exclude_name_contains: list[str] = Field(default_factory=list)
    exclude_folders: list[str] = Field(default_factory=list)
    filename_pattern: str | None = None
    prefer_extension: str | None = None
    scope: str | None = None
    highest_precedence_for_solids: bool = False

    @field_validator("latest_n")
    @classmethod
    def validate_latest_n(cls, value: int | None) -> int | None:
        """Require a positive count when latest_n is provided."""
        if value is not None and value < 1:
            raise ValueError("latest_n must be greater than zero.")
        return value

    @field_validator("filename_pattern")
    @classmethod
    def validate_filename_pattern(cls, value: str | None) -> str | None:
        """Ensure regex patterns fail early if invalid."""
        if value is None:
            return value
        try:
            re.compile(value)
        except re.error as exc:
            raise ValueError(f"Invalid filename_pattern regex: {exc}") from exc
        return value

    @field_validator("prefer_extension")
    @classmethod
    def validate_prefer_extension(cls, value: str | None) -> str | None:
        """Normalize and validate preferred file extensions."""
        if value is None:
            return value
        cleaned = value.strip()
        if not cleaned.startswith(".") or len(cleaned) == 1:
            raise ValueError("prefer_extension must be a file extension such as '.xlsm'.")
        return cleaned.lower()

    @model_validator(mode="after")
    def validate_selection_mode(self) -> "SelectionRules":
        """Prevent conflicting primary selection modes."""
        active_modes = sum(
            (
                bool(self.latest_only),
                self.latest_n is not None,
                bool(self.latest_per_day),
            )
        )
        if active_modes > 1:
            raise ValueError(
                "Only one primary selection mode is supported per source: "
                "latest_only, latest_n, or latest_per_day."
            )
        return self


class SourceDefinition(StrictBaseModel):
    """A configured data source from the approved source manifest."""

    source_id: str
    source_name: str
    source_type: SourceType
    site_scope: str
    plant_scope: str
    domain: str
    path: Path | None = None
    mailbox_scope: str | None = None
    subject_patterns: list[str] = Field(default_factory=list)
    selection_rules: SelectionRules = Field(default_factory=SelectionRules)
    enabled: bool = True
    authoritative_for: list[str] = Field(default_factory=list)
    notes: str | None = None
    expected_refresh: str | None = None
    timestamp_strategy: str | None = None

    @model_validator(mode="after")
    def validate_source_shape(self) -> "SourceDefinition":
        """Require only the fields that make sense for the source type."""
        if self.source_type == SourceType.EMAIL:
            if not self.mailbox_scope:
                raise ValueError("Email sources must define mailbox_scope.")
            if not self.subject_patterns:
                raise ValueError("Email sources must define at least one subject pattern.")
        else:
            if self.path is None:
                raise ValueError(f"{self.source_type.value} sources must define path.")
            if self.mailbox_scope is not None:
                raise ValueError("Only email sources may define mailbox_scope.")
            if self.subject_patterns:
                raise ValueError("Only email sources may define subject_patterns.")
        return self


class Exclusions(StrictBaseModel):
    """Manifest-wide exclusions applied before source-specific rules."""

    sharepoint_paths: list[str] = Field(default_factory=list)
    filename_contains: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class SourceManifest(StrictBaseModel):
    """Top-level source manifest loaded from sources.yaml."""

    site: str
    plant_scope: str
    sources: list[SourceDefinition]
    exclusions: Exclusions = Field(default_factory=Exclusions)

    @model_validator(mode="after")
    def validate_unique_source_ids(self) -> "SourceManifest":
        """Fail fast when a manifest repeats a source_id."""
        seen: set[str] = set()
        duplicates: list[str] = []
        for source in self.sources:
            if source.source_id in seen:
                duplicates.append(source.source_id)
            seen.add(source.source_id)
        if duplicates:
            duplicate_list = ", ".join(sorted(set(duplicates)))
            raise ValueError(f"Duplicate source_id values are not allowed: {duplicate_list}")
        return self


class DomainPrecedenceRule(StrictBaseModel):
    """Domain-specific source precedence list."""

    preferred_sources: list[str]
    notes: list[str] = Field(default_factory=list)

    @field_validator("preferred_sources")
    @classmethod
    def validate_preferred_sources(cls, value: list[str]) -> list[str]:
        """Require at least one preferred source per domain."""
        if not value:
            raise ValueError("preferred_sources must contain at least one source_id.")
        return value


class PrecedenceRules(StrictBaseModel):
    """Root model for precedence_rules.yaml."""

    precedence: dict[str, DomainPrecedenceRule]


class RefreshRule(StrictBaseModel):
    """Freshness rule for a configured source."""

    source_id: str
    metric: RefreshMetric
    warning_threshold: int
    error_threshold: int

    @model_validator(mode="after")
    def validate_thresholds(self) -> "RefreshRule":
        """Require positive thresholds ordered from warning to error."""
        if self.warning_threshold < 0 or self.error_threshold < 0:
            raise ValueError("warning_threshold and error_threshold must be non-negative.")
        if self.error_threshold < self.warning_threshold:
            raise ValueError("error_threshold must be greater than or equal to warning_threshold.")
        return self


class RefreshRules(StrictBaseModel):
    """Root model for refresh_rules.yaml."""

    rules: list[RefreshRule]

