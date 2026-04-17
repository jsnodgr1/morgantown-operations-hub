# North Plant Daily Operations – Source Inventory

This document defines the authoritative data sources used to generate the
**Daily North Plant Operational Status** report.

Only North Plant sources are in scope. South Plant artifacts are explicitly excluded.

---

## Tier‑1 Required Sources (Daily)

### 1. Daily Manufacturing Review
- **Type**: Excel
- **Canonical Name**: `Daily Manufacturing Review.xlsx`
- **Purpose**: Lagging KPIs and actual vs schedule performance
- **Source System**: SharePoint
- **Frequency**: Daily (single active file)
- **Used For**:
  - Safety, quality, delivery, production KPIs
  - Validation of operational narrative

---

### 2. Master North Plant Liquids Schedule
- **Type**: Excel (macro-enabled)
- **Canonical Name**: `Master North Plant Liquids Schedule.xlsm`
- **Purpose**: Liquids production plan, inventory outlook, liquid shipments
- **Source System**: SharePoint
- **Frequency**: Continuously updated
- **Selection Rule**:
  - Use most recently modified **non-archived** version

---

### 3. Blends Schedule
- **Type**: Excel (macro-enabled)
- **Canonical Name**: `Blends Schedule.xlsm`
- **Purpose**: Blends campaign planning
- **Source System**: SharePoint
- **Frequency**: Continuously updated

---

### 4. Master Solids Schedule
- **Type**: Excel (macro-enabled)
- **Canonical Name**: `Master Solids Schedule.xlsm`
- **Purpose**: Solids / flaking production plan
- **Source System**: SharePoint
- **Frequency**: Continuously updated

---

### 5. Shipping Schedules (Folder Content)
- **Type**: Excel
- **Canonical Location**: `Operations → Schedules (Weekly-Daily) → Shipping Schedule`
- **Purpose**: Customer delivery commitments
- **Selection Rule**:
  - Use the **latest two** dated shipping schedule files only
  - Ignore older and archived schedules

---

## Shift Instruction Streams (Email + Docs)

### 6. North Plant Shift Instructions
- **Type**: Word or Email
- **Canonical Pattern**: `North Plant Shift Instructions <date>`
- **Purpose**: Liquids execution status and constraints
- **Frequency**: Daily
- **Selection Rule**:
  - Use the most recent instruction for the report date

---

### 7. Blends Shift Instructions
- **Type**: Email
- **Canonical Subject Pattern**: `Blends Shift Instructions <date>`
- **Purpose**: Blends execution intent, discipline issues, local constraints
- **Frequency**: Daily

---

### 8. K9 / 195 Evening News
- **Type**: Email
- **Canonical Subject Pattern**: `K9/195 Evening News <date>`
- **Purpose**: Solids execution reality, rate limits, equipment constraints
- **Frequency**: Daily (late afternoon / evening)

---

## Explicit Exclusions

- South Plant schedules and instructions
- Archived schedules unless explicitly required
- Historical planning documents older than the report date window

---

## Precedence Summary

Execution truth is determined in the following order:
1. Shift Instructions / Evening News
2. Schedules
3. Daily Manufacturing Review