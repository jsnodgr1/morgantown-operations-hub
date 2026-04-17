# Canonical Schema

This document defines the canonical business entities used by normalization, reconciliation, and snapshot generation. It is intentionally separate from any eventual output formatting or report layout.

The canonical schema should stay small, explicit, and traceable. V1 only needs enough structure to support the current pipeline and `StateSnapshot` assembly.

## Entity Summary

| Entity | Key Fields | Definition |
| --- | --- | --- |
| Area | `area_id`, `area_name`, `area_group` | Canonical production area or operating zone used across sources after normalization. |
| Product | `product_code`, `product_name`, `product_family` | Canonical product identity used to reconcile plan and actual data. |
| Campaign/Run | `run_id`, `area_id`, `product_code`, `start_time`, `end_time`, `status` | Optional run-level concept for sources that identify a discrete campaign or run. |
| ActualProduction | `area_id`, `product_code`, `quantity`, `unit`, `observed_at`, `source_id` | Observed or reported production state from an actuals-oriented source. |
| PlanTarget | `area_id`, `product_code`, `quantity`, `unit`, `period`, `source_id` | Planned target for a defined period, such as daily, monthly, or annual. |
| Issue | `code`, `severity`, `message`, `source_id`, `context` | Validation, freshness, or reconciliation finding tied to snapshot trust. |
| StateSnapshot | `facility_id`, `generated_at`, `actuals`, `plans`, `issues`, `source_freshness` | Consolidated point-in-time operating state produced by the pipeline. |

## Interpretation Notes

- `ActualProduction`, `PlanTarget`, and `Issue` are canonical records, not source-shaped rows.
- `StateSnapshot` is the canonical assembled output of the pipeline. It is not a presentation template.
- `Campaign/Run` should only be populated when a V1 source reliably supports run-level interpretation.

## Traceability Expectations

- Every business value in the snapshot should remain traceable to a source and a rule path.
- Time-bearing entities should distinguish between extraction time and business-effective time when both exist.
- Canonical identifiers should remain stable even when source labels drift.

## Open Decisions

- TODO: confirm whether `Campaign/Run` is required in the first real V1 dataset or remains optional
- TODO: confirm which longer-horizon `PlanTarget.period` values remain in V1
- TODO: confirm whether additional source-trace fields are needed on canonical records beyond the current scaffold
