"""Typed models used across the initial pipeline scaffold."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class Severity(str, Enum):
    """Supported issue severities for validation and reconciliation."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class SourceConfig(BaseModel):
    """Configuration for a single workbook-like source."""

    source_id: str
    source_name: str
    source_type: str
    path: Path
    sheet_names: list[str] = Field(default_factory=list)
    enabled: bool = True
    owner: str | None = None
    refresh_expectation: str | None = None
    timestamp_strategy: str | None = None


class ActualProduction(BaseModel):
    """Canonical actual production observation."""

    area_id: str
    product_code: str
    quantity: float
    unit: str
    source_id: str
    observed_at: datetime | None = None


class PlanTarget(BaseModel):
    """Canonical production target for a time period."""

    area_id: str
    product_code: str
    quantity: float
    unit: str
    period: str
    source_id: str


class Issue(BaseModel):
    """Validation or reconciliation finding."""

    code: str
    message: str
    severity: Severity
    source_id: str | None = None
    context: dict[str, Any] = Field(default_factory=dict)


class SourceFreshness(BaseModel):
    """Freshness status for a configured source."""

    source_id: str
    checked_at: datetime
    is_stale: bool
    note: str | None = None


class StateSnapshot(BaseModel):
    """Consolidated point-in-time operating state."""

    facility_id: str
    generated_at: datetime
    actuals: list[ActualProduction] = Field(default_factory=list)
    plans: list[PlanTarget] = Field(default_factory=list)
    issues: list[Issue] = Field(default_factory=list)
    source_freshness: list[SourceFreshness] = Field(default_factory=list)
