# Daily North Plant Operational Status – Schema

The Daily Output represents a single consolidated operational view for one
North Plant operating day.

This schema is both human-readable and machine-consumable.

---

## 1. Report Metadata

```yaml
report_metadata:
  site: Morgantown
  plant_scope: North Plant
  report_date: YYYY-MM-DD
  report_generated_timestamp: ISO-8601
  source_versions:
    liquids_schedule_last_modified: timestamp
    blends_schedule_last_modified: timestamp
    solids_schedule_last_modified: timestamp
    shipping_schedule_last_modified: timestamp
    shift_instructions_date: YYYY-MM-DD
    blends_shift_email_date: YYYY-MM-DD
    k9_195_evening_news_date: YYYY-MM-DD
``
executive_summary:
  overall_status: Green | Yellow | Red
  confidence_score: 0.0 – 1.0
  one_line_summary: string

  kpis:
  safety: {}
  quality: {}
  delivery: {}
  production: {}

liquids:
  plan: {}
  execution:
    running_units: []
    down_units: []
  issues: []
  status: On Plan | Degraded | Not Running

solids:
  plan: {}
  execution:
    actual_rate_lbs_per_min: number
  constraints: []
  near_term_outlook:
    last_batch_before_pm: boolean
  status: On Plan | Rate Limited | Not Running

blends:
  plan: {}
  execution: {}
  discipline_flags:
    missing_logs: boolean
    pause_observations_due: boolean
    papr_inspection_due: boolean
  issues: []
  status: On Plan | Degraded | Not Running

shipping:
  planned_shipments: []
  execution_notes: []
  customer_risk:
    overall_risk: Low | Medium | High
    drivers: []
``
cross_area_impacts:
  - source_area: string
    impacted_area: string
    description: string

    risks: []
recommendations: []
``

---

# ✅ `docs/extraction_rules.md`

```markdown
# Data Extraction Rules

This document defines deterministic extraction behavior for each source.

Schedules define the **plan**.
Shift instructions define **execution truth**.

---

## Global Rules

- Always select the most recently modified valid file
- Normalize all dates to YYYY-MM-DD
- Extract numeric values with units preserved
- Never assume missing information
- Execution overrides plan

---

## Daily Manufacturing Review

- Extract KPI value from the column matching report_date day-of-month
- Map values directly into KPI fields
- Do not normalize percentages above 100%

---

## Liquids Schedule

- Select newest non-archived file
- Extract only rows relevant to report_date window
- Map inventory EOD fields
- Treat shipment references as *planned*, not executed

---

## Blends Schedule

- Extract planned campaigns by date
- Ignore historical blocks outside current window
- Preserve process order and notes

---

## Master Solids Schedule

- Extract scheduled products and batch identifiers
- Do not infer rates from plan
- Use comments verbatim

---

## Shipping Schedules

### Dated Shipping Files
- Load latest two files only
- Deduplicate by document number and ship-to
- Flag zero confirmed quantity as risk

### SHIPPING SCHEDULE.xlsm
- Treat rows as execution-level events
- Preserve carrier, arrival time, and comments

---

## North Plant Shift Instructions

- Parse unit RUN / Down table
- Extract issues from Notes section
- Parse any “Trucks” sections into shipping execution notes

---

## Blends Shift Instructions

- If short-form:
  - Populate discipline flags only
- If detailed:
  - Extract running campaigns
  - Capture equipment and process warnings

---

## K9 / 195 Evening News

- Extract actual production rate (regex: Running (\d+) lb/min)
- Parse equipment constraints
- Capture “last batch” statements verbatim
- Create cross-area impact when assistance is requested