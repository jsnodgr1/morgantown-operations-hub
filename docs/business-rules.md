# Business Rules

This document is the decision log for rules that must be made explicit in code or configuration. If a rule matters to extraction, normalization, reconciliation, snapshot generation, or QA, record it here before relying on it in implementation.

If a decision is still open, leave a `TODO` instead of silently assuming behavior.

## Source Precedence

Define which source is authoritative for each business field used in the canonical snapshot.

Current status:

- the approved V1 source manifest now establishes first-pass domain-specific precedence
- `config/precedence_rules.yaml` should be treated as the executable starting point for those domain-specific rules

Open decisions:

- TODO: define precedence for current product
- TODO: confirm field-level precedence within shipping execution versus shipping plan
- TODO: define precedence for longer-horizon plan values, if those remain in V1
- TODO: define tie-breakers when sources disagree but have similar freshness

## Stale Source Thresholds

Define freshness expectations by source so QA can flag stale or missing inputs consistently.

Current status:

- freshness thresholds are not business-approved yet
- `config/refresh_rules.yaml` contains example thresholds only

Open decisions:

- TODO: define freshness thresholds per V1 source
- TODO: define whether workbook modified time is acceptable when no business timestamp exists
- TODO: define whether any stale source is blocking versus warning-only

## Schedule Vs Actual Reconciliation

Define how planned and actual production signals are compared and when they should be treated as conflicting.

Current status:

- the code scaffold currently compares daily plan versus actual quantity at a simple level
- the business meaning of `current product` and `current run state` is still open

Open decisions:

- TODO: define what counts as the current product for an area
- TODO: define how to handle lag between plan updates and actual updates
- TODO: define quantity variance tolerances, if quantity comparison remains part of V1
- TODO: define whether missing plan or missing actual is always an issue

## Product, Area, And Unit Normalization

Define the rules used to turn source-specific labels into canonical identifiers and units.

Current status:

- the repo includes crosswalk files for areas, products, and units
- the acceptance rules for automatic mapping versus explicit rejection are not defined yet

Open decisions:

- TODO: define required canonical identifiers for areas and products
- TODO: define when an unmapped source label should block the snapshot
- TODO: define approved unit conversions and any prohibited conversions

## Manual Overrides

Define whether V1 allows manual override inputs that can change reconciled state.

Current status:

- no override mechanism is defined in the current scaffold

Open decisions:

- TODO: decide whether manual overrides are in scope for V1
- TODO: if overrides are allowed later, define storage, ownership, and audit expectations

## Issue Severity Logic

Define how issues are classified so QA results are consistent and explainable.

Current status:

- the code scaffold supports `info`, `warning`, and `error`
- the blocking threshold for publication is not defined yet

Open decisions:

- TODO: define which conditions are informational versus warning versus error
- TODO: define which issue types block publication of a snapshot
- TODO: define whether stale but still readable inputs are warning or error conditions

## Conflict Handling

Define what the pipeline should do when multiple sources disagree.

This section should describe conflict handling for canonical business fields only. It should not define presentation formatting or end-user report layout.

Open decisions:

- TODO: define when the system chooses a winner automatically
- TODO: define when the system must surface an unresolved conflict in the snapshot
- TODO: define what traceability details must be retained for each conflict decision
