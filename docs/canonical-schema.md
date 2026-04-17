# Canonical Schema

The initial canonical schema should stay small, explicit, and traceable. The entities below define the first-pass model for a daily operating snapshot.

## Entities

| Entity | Key Fields | Definition |
| --- | --- | --- |
| Area | `area_id`, `area_name`, `area_group` | Canonical production area or operating zone used across all sources. |
| Product | `product_code`, `product_name`, `product_family` | Canonical product identity used to reconcile plan and actual data. |
| Campaign/Run | `run_id`, `area_id`, `product_code`, `start_time`, `end_time`, `status` | A discrete production run or campaign segment when source data supports it. |
| ActualProduction | `area_id`, `product_code`, `quantity`, `unit`, `observed_at`, `source_id` | Observed or reported production state from an actuals-oriented source. |
| PlanTarget | `area_id`, `product_code`, `quantity`, `unit`, `period`, `source_id` | Planned production target for a defined period such as day, month, or year. |
| Issue | `code`, `severity`, `message`, `source_id`, `context` | A validation, freshness, or reconciliation finding tied to snapshot trust. |
| StateSnapshot | `facility_id`, `generated_at`, `actuals`, `plans`, `issues`, `source_freshness` | Consolidated point-in-time operating state produced by the pipeline. |

## Notes

- Every business value in the snapshot should be traceable back to a source and rule path.
- Time-bearing entities should distinguish between extraction time and business-effective time.
- Canonical identifiers should remain stable even when source labels drift.
