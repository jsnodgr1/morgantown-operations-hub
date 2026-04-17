# V1 Scope

## Milestone

Produce one validated daily operating snapshot from a small approved set of core workbook sources.

## Pipeline Boundary

The current V1 boundary is:

1. inventory sources
2. extract configured workbook content
3. normalize source-specific values into canonical forms
4. reconcile plan-versus-actual state
5. assemble one `StateSnapshot`
6. run QA and validation checks before the snapshot is trusted

This document defines scope for that pipeline. It does not define presentation layout, downstream report formatting, or plant-specific briefing structure.

## In Scope

- load a small, explicitly configured set of local Excel workbooks
- extract a limited set of tabs and fields needed for a daily facility snapshot
- capture source-level metadata needed for traceability and freshness checks
- normalize source-specific area, product, and unit labels into canonical forms
- reconcile schedule-versus-actual production state using explicit precedence rules
- generate one canonical snapshot with source freshness and issue records
- provide validation checks that flag stale, missing, conflicting, or unmapped source data

## Out Of Scope

- automated writeback to source systems or source workbooks
- browser UI, dashboards, slide decks, or email-format outputs
- historical trend storage beyond a single generated snapshot artifact
- generalized support for every workbook used at the facility
- optimization, forecasting, or advanced planning logic

## Initial Source Candidates

The approved V1 source manifest is North Plant-focused within Morgantown and should be documented in `docs/source-inventory.md` and encoded in `config/sources.yaml`.

Approved V1 source groups:

- liquids schedule
- blends schedule
- solids schedule
- shipping execution log
- shipping dated schedules
- daily manufacturing review
- North Plant shift instructions
- blends shift instructions
- K9/195 Evening News

## Initial Outputs

- one consolidated daily operating snapshot
- source freshness status by configured source
- issue records describing conflicts, missing values, stale inputs, and rule-driven warnings

## Risks

- workbook layouts may drift without notice
- manual edits may change meaning without changing file structure
- cached formula values may not reflect the latest workbook state
- source precedence can be business-specific and contested
- unit and product naming inconsistencies can cause silent reconciliation errors
- undefined source authority can leak into code as implicit assumptions

## Validation Approach

- start with a small set of known workbook samples
- document source assumptions before encoding extraction or reconciliation logic
- create focused unit tests for normalization and reconciliation decisions
- compare generated snapshots against analyst-reviewed expectations
- treat unexplained conflicts and missing mappings as issues, not silent fallbacks

## Open Decisions

- TODO: confirm owner names and mailbox or SharePoint access details for each approved source
- TODO: confirm which fields are authoritative versus supporting for each source
- TODO: confirm freshness thresholds by source
- TODO: confirm what conditions should block publication of a snapshot
