"""Quality checks that should run before a snapshot is trusted."""

from __future__ import annotations

from morgantown_ops_hub.models import Issue, Severity, StateSnapshot


def evaluate_snapshot_quality(snapshot: StateSnapshot) -> list[Issue]:
    """Return simple QA findings for an assembled snapshot."""
    findings: list[Issue] = []

    if not snapshot.actuals:
        findings.append(
            Issue(
                code="no_actuals_loaded",
                message="Snapshot contains no actual production records.",
                severity=Severity.ERROR,
            )
        )

    stale_sources = [item.source_id for item in snapshot.source_freshness if item.is_stale]
    if stale_sources:
        findings.append(
            Issue(
                code="stale_sources_present",
                message="One or more configured sources are stale.",
                severity=Severity.WARNING,
                context={"source_ids": stale_sources},
            )
        )

    return findings
