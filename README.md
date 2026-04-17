# Morgantown Operations Hub

`morgantown-operations-hub` is a Windows-friendly Python application scaffold for consolidating volatile workbook-based operational data into a single daily view of manufacturing state for the Morgantown facility.

The hub is intended to ingest multiple Excel sources, normalize inconsistent labels and units, reconcile schedule-versus-actual production signals, and emit a consolidated operating snapshot with traceable issues and freshness context.

## Questions The Hub Should Answer

- What is the facility producing right now, by area and product?
- What was scheduled for today versus what appears to have actually run?
- Which sources disagree, and which source currently wins for each business field?
- Are any critical source files stale or missing?
- Which assumptions, crosswalks, and reconciliation rules materially affected the final snapshot?

## Initial Architecture Overview

The first version is designed as a local Python pipeline with explicit stages:

1. `extract`: discover configured sources and load workbook data.
2. `normalize`: standardize column names, labels, and units into canonical forms.
3. `reconcile`: compare planned and actual production state using explicit precedence and freshness rules.
4. `snapshot`: assemble a validated point-in-time state object for downstream reporting.
5. `qa`: surface issues, stale inputs, and rule-driven warnings before outputs are trusted.

Configuration and business logic are intentionally separated:

- `config/` stores source definitions, refresh expectations, and precedence hints.
- `mappings/` stores controlled crosswalk tables for areas, products, and units.
- `docs/` captures scope, schema, and business rule decisions that should be reflected in code.

## Current V1 Scope

V1 is focused on producing one validated daily operating snapshot from a small set of core workbook sources on a local Windows workstation.

Included in this initial scaffold:

- project structure for source, config, mappings, docs, samples, tests, and outputs
- starter typed models and logging utilities
- module boundaries for extract, normalize, reconcile, snapshot, QA, and Excel IO
- baseline config and documentation templates

## Non-Goals For V1

- no web UI, API, or background service
- no database or cloud deployment layer
- no attempt to automate every workbook variation up front
- no silent business logic embedded in spreadsheets without corresponding code or config rules
- no writeback into source workbooks

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

Run the current scaffold entry point:

```powershell
python -m morgantown_ops_hub.main
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

Every consolidated snapshot should eventually preserve:

- the exact source file and sheet used
- the extraction timestamp
- the business timestamp taken from the source, when available
- the freshness evaluation applied to that source
- the rule or precedence decision used when conflicting values exist

This project should treat timestamps as first-class data, not incidental metadata. A snapshot is only useful if its recency and provenance are obvious.

## Reliability Notes

Workbook logic should not be trusted blindly. Spreadsheet formulas, hidden tabs, cached values, and manual edits can drift over time. All normalization, precedence, reconciliation, and issue-severity rules should be made explicit in code and configuration so that the operating snapshot is explainable and reviewable.
