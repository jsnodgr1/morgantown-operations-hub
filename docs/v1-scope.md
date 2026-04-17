# V1 Scope

## Milestone

Produce one validated daily operating snapshot from a small set of core workbook sources.

## In Scope

- load a small, explicitly configured set of local Excel workbooks
- extract a limited set of tabs and fields needed for a daily facility snapshot
- normalize source-specific area, product, and unit labels into canonical forms
- reconcile schedule-versus-actual production state using explicit precedence rules
- generate a single state snapshot with issues, freshness context, and traceability
- provide validation checks that flag stale, missing, or conflicting source data

## Out Of Scope

- automated writeback to source systems or workbooks
- browser UI, dashboards, or APIs
- historical trend storage beyond a single generated snapshot artifact
- generalized support for every workbook used at the facility
- optimization, forecasting, or advanced planning logic

## Initial Source Candidates

- daily production schedule workbook
- shift or operations handoff workbook
- actual production tracker workbook
- area-specific planning or campaign workbook

## Initial Outputs

- one consolidated daily operating snapshot
- source freshness status by configured source
- issue list describing conflicts, missing values, and rule-driven warnings

## Risks

- workbook layouts may drift without notice
- manual edits may change meaning without changing file structure
- cached formula values may not reflect the latest workbook state
- source precedence can be business-specific and contested
- unit and product naming inconsistencies can cause silent reconciliation errors

## Validation Approach

- start with a small set of known workbook samples
- document source assumptions before encoding rules
- create focused unit tests for normalization and reconciliation decisions
- compare generated snapshots against analyst-reviewed expectations
- treat unexplained conflicts as issues, not silent fallbacks
