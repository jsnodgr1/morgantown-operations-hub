"""Snapshot assembly helpers."""

from __future__ import annotations

from datetime import datetime, timezone

from morgantown_ops_hub.models import ActualProduction, Issue, PlanTarget, SourceFreshness, StateSnapshot


def build_state_snapshot(
    facility_id: str,
    actuals: list[ActualProduction],
    plans: list[PlanTarget],
    issues: list[Issue],
    source_freshness: list[SourceFreshness] | None = None,
) -> StateSnapshot:
    """Construct a canonical point-in-time state snapshot."""
    return StateSnapshot(
        facility_id=facility_id,
        generated_at=datetime.now(timezone.utc),
        actuals=actuals,
        plans=plans,
        issues=issues,
        source_freshness=source_freshness or [],
    )
