# Morgantown Operations Hub

`morgantown-operations-hub` is a Windows-friendly Python application for consolidating volatile workbook-based operational data into one validated daily operating snapshot for the Morgantown facility.

The current repo is intentionally narrow. V1 is a local pipeline that reads a small set of configured workbook sources, normalizes them into a canonical model, reconciles schedule-versus-actual state, and assembles a traceable snapshot with QA findings and source freshness context. The site scope is Morgantown, and the current active operating scope corresponds to the former North Plant footprint. South Plant content is excluded because it is mothballed legacy scope. `North Plant` still appears in source names where that remains the operational label.

## Questions The Hub Should Answer

- What is the facility producing now, by area and product?
- What was planned for the day versus what the current actuals-oriented sources indicate?
- Which sources are stale, missing, or in conflict?
- Which source won for a given field, and why?
- Which explicit mappings, precedence decisions, and validation checks affected the snapshot?

## V1 Architecture

V1 follows six practical stages that map directly to the current package structure:

1. `source inventory`: document candidate workbook sources, owners, refresh expectations, and likely authority.
2. `extract`: load configured workbook files and target sheets.
3. `normalize`: standardize source-specific headers, labels, and units into canonical forms.
4. `reconcile`: compare planned and actual production state using explicit precedence and freshness rules.
5. `snapshot`: assemble a point-in-time canonical `StateSnapshot`.
6. `qa/validation`: flag stale inputs, missing values, and unresolved conflicts before the snapshot is trusted.

The repo keeps these concerns separate on purpose:

- `docs/` records scope, canonical concepts, and unresolved rule decisions.
- `config/` records executable source definitions and starter rules.
- `mappings/` records crosswalk data used during normalization.
- `src/morgantown_ops_hub/` contains the implementation scaffold for the pipeline stages above.

## Current V1 Scope

V1 is limited to producing one validated daily operating snapshot from a small set of local workbook sources on a Windows workstation.

In scope:

- explicit source inventory and source configuration
- workbook extraction for a limited set of tabs and fields
- canonical normalization of areas, products, and units
- schedule-versus-actual reconciliation
- snapshot assembly with source freshness and issue tracking
- targeted tests around normalization, reconciliation, and snapshot creation

## Non-Goals For V1

- no web UI, API, or background service
- no database or long-term history layer
- no writeback into source workbooks or external systems
- no attempt to generalize every workbook pattern up front
- no implicit business rules hidden only in spreadsheets

## Local Setup

On Windows PowerShell:

```powershell
py -3.10 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e .
```

## Run Instructions

Validate the current config bundle:

```powershell
python -m morgantown_ops_hub.main --config-dir config
```

Run a local dry source-resolution pass against the sanitized sample fixture and write an artifact to `output/source_resolution_dry_run.json`:

```powershell
python -m morgantown_ops_hub.main --config-dir config --dry-run-resolution --candidate-fixture samples/source_candidates_fixture.json --output-dir output
```

Run tests:

```powershell
python -m pytest
```

If you prefer not to install the package in editable mode, set the source path for `src/`-layout imports during local development:

```powershell
$env:PYTHONPATH = "src"
python -m pytest
```

## Traceability, Timestamps, And Source Freshness

Every published snapshot should preserve or derive, when possible:

- the source file path and source identifier
- the workbook sheet or tab used
- the extraction timestamp
- the business timestamp taken from the source, when available
- the freshness evaluation applied to that source
- the rule or precedence decision used when conflicting values exist

Timestamps are part of the business meaning of the snapshot, not just system metadata. A daily snapshot is not trustworthy if the recency and provenance of its inputs are unclear.

## Documentation Map

- `docs/v1-scope.md`: what V1 is and is not trying to do
- `docs/source-inventory.md`: source-by-source inventory used to drive `config/sources.yaml`
- `docs/business-rules.md`: explicit rule decisions and TODOs for precedence, freshness, reconciliation, and issue handling
- `docs/canonical-schema.md`: canonical entities used by normalization, reconciliation, and snapshot assembly

## Reliability Notes

Workbook logic should not be trusted blindly. Hidden tabs, cached formula values, manual edits, and naming drift can all change behavior without changing intent. Normalization rules, precedence rules, and QA criteria should therefore be explicit in code or config so the resulting snapshot stays explainable and reviewable.
