# Business Rules

This document is the decision log for operational rules that must be mirrored in code and configuration.

## Source Precedence

- Define which source is authoritative for each business field.
- Record tie-breakers when multiple sources are equally fresh.

## Stale Source Thresholds

- Define freshness expectations by source.
- Note any different thresholds for weekdays, shift boundaries, or monthly planning files.

## Schedule Vs Actual Reconciliation

- Define what constitutes "current product" and "current run state."
- Define how to handle lag between planned and actual updates.
- Define tolerance thresholds for quantity variances.

## Product And Area Crosswalk Rules

- Record naming mismatches and canonical mappings.
- Document when a source-specific alias should be rejected instead of mapped automatically.

## Unit Conversion Rules

- Define standard units for output.
- Document approved conversion factors and any prohibited conversions.

## Manual Overrides

- Define who can override reconciled state.
- Define where overrides are stored and how they are audited.

## Issue Severity Logic

- Define when an issue is informational, warning, or error severity.
- Define which issues should block publication of a daily snapshot.

## Conflict Handling

- Define expected behavior for conflicting schedule, target, or issue-state values.
- Define when the system should choose a winner versus escalating the conflict explicitly.
