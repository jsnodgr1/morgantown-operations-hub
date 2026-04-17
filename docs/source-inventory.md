# Source Inventory

This document is the human-readable V1 source inventory for the approved Morgantown Operations Hub source manifest.

V1 source scope is explicitly North Plant-focused within Morgantown. South Plant content and archived content are excluded unless a later approved change says otherwise.

Latest modified timestamp is useful for file selection, but it is not by itself proof of business freshness. Freshness still needs source-aware validation.

Precedence is domain-specific. Do not treat any one source as a globally universal winner across every business field.

## Approved V1 Sources

### Master North Plant Liquids Schedule

- Source id: `liquids_schedule`
- Location/path or mailbox/subject pattern: `Morgantown/Operations/Schedules (Weekly-Daily)/Master North Plant Liquids Schedule.xlsm`
- Business purpose: North Plant liquids planning and schedule context
- Source category: SharePoint workbook
- Candidate classification: `authoritative`
- Selection rules: latest eligible file only; exclude names containing `Archive`; North Plant scope only
- Likely authoritative fields: North Plant liquids planned schedule context
- Refresh cadence: `TODO`
- Timestamp fields: `TODO`; latest modified time may be used for file selection only
- Known risks / manual-edit concerns: workbook edits may change without explicit versioning; archive naming must stay excluded
- Precedence notes: use within the planned schedule domain and as supporting context for current North Plant execution state
- Open questions / TODOs: confirm tabs or sheets used; confirm business timestamp field; confirm refresh cadence

### Blends Schedule

- Source id: `blends_schedule`
- Location/path or mailbox/subject pattern: `Morgantown/Operations/Schedules (Weekly-Daily)/Blends Schedule.xlsm`
- Business purpose: blends planning and schedule context
- Source category: SharePoint workbook
- Candidate classification: `authoritative`
- Selection rules: latest eligible file only
- Likely authoritative fields: blends planned schedule context
- Refresh cadence: `TODO`
- Timestamp fields: `TODO`; latest modified time may be used for file selection only
- Known risks / manual-edit concerns: workbook content may change without a business-date change; tabs in scope are still undefined
- Precedence notes: scheduled source for the blends domain; lower precedence than `blends_shift_instructions` for blends execution state
- Open questions / TODOs: confirm tabs or sheets used; confirm business timestamp field; confirm refresh cadence

### Master Solids Schedule

- Source id: `solids_schedule`
- Location/path or mailbox/subject pattern: `Morgantown/Operations/Schedules (Weekly-Daily)/Master Solids Schedule.xlsm`
- Business purpose: solids planning and schedule context
- Source category: SharePoint workbook
- Candidate classification: `authoritative`
- Selection rules: latest eligible file only; prefer `.xlsm`
- Likely authoritative fields: solids planned schedule context
- Refresh cadence: `TODO`
- Timestamp fields: `TODO`; latest modified time may be used for file selection only
- Known risks / manual-edit concerns: workbook naming variants may exist; tabs in scope are still undefined
- Precedence notes: scheduled source for the solids domain; lower precedence than `k9_195_evening_news` for solids execution state
- Open questions / TODOs: confirm tabs or sheets used; confirm business timestamp field; confirm refresh cadence

### SHIPPING SCHEDULE Execution Log

- Source id: `shipping_execution_log`
- Location/path or mailbox/subject pattern: `Morgantown/Operations/Schedules (Weekly-Daily)/Shipping Schedule/SHIPPING SCHEDULE.xlsm`
- Business purpose: shipping execution status and same-day shipping activity context
- Source category: SharePoint workbook
- Candidate classification: `authoritative`
- Selection rules: latest eligible file only; exclude folder `Archive`
- Likely authoritative fields: shipping execution state
- Refresh cadence: `TODO`
- Timestamp fields: `TODO`; latest modified time may be used for file selection only
- Known risks / manual-edit concerns: operational workbook may be edited throughout the day; execution log versus dated shipping plan still needs field-level confirmation
- Precedence notes: first-pass source for `shipping_execution`; not a globally universal shipping winner for every shipping field
- Open questions / TODOs: confirm tabs or sheets used; confirm business timestamp field; confirm exact authority versus dated schedules

### Shipping Dated Schedules

- Source id: `shipping_dated_schedules`
- Location/path or mailbox/subject pattern: `Morgantown/Operations/Schedules (Weekly-Daily)/Shipping Schedule` with filename pattern `\d{8} Schedule.xlsm`
- Business purpose: dated shipping plan and near-term shipping commitment context
- Source category: SharePoint folder
- Candidate classification: `authoritative`
- Selection rules: include the latest two files matching `\d{8} Schedule.xlsm`; exclude folder `Archive`
- Likely authoritative fields: shipping plan
- Refresh cadence: `TODO`
- Timestamp fields: `TODO`; file dates and modified times are not by themselves proof of business freshness
- Known risks / manual-edit concerns: multiple dated files can coexist; folder hygiene and archive handling matter
- Precedence notes: first-pass source group for `shipping_plan`; lower priority than `shipping_execution_log` for execution-only questions
- Open questions / TODOs: confirm whether only filename date matters or an in-workbook date also exists; confirm tabs or sheets used

### Daily Manufacturing Review

- Source id: `daily_manufacturing_review`
- Location/path or mailbox/subject pattern: `Morgantown/Operations/Manufacturing Review/Daily Manufacturing Review.xlsx`
- Business purpose: daily manufacturing summary and KPI-oriented review context
- Source category: SharePoint workbook
- Candidate classification: `derivative`
- Selection rules: latest eligible file only
- Likely authoritative fields: daily summary or KPI-oriented review fields where specifically approved
- Refresh cadence: daily
- Timestamp fields: `TODO`; confirm workbook review date field
- Known risks / manual-edit concerns: summary workbooks may lag behind execution-specific sources and may aggregate data from other sources
- Precedence notes: summary-oriented source; should not automatically outrank execution-specific sources for same-day operational state
- Open questions / TODOs: confirm which fields are treated as authoritative versus supporting; confirm tabs or sheets used

### North Plant Shift Instructions

- Source id: `north_plant_shift_instructions`
- Location/path or mailbox/subject pattern: mailbox scope `Operations`; subject contains `North Plant Shift Instructions`
- Business purpose: North Plant execution guidance and same-day operating context
- Source category: Email
- Candidate classification: `authoritative`
- Selection rules: latest matching message per day
- Likely authoritative fields: current North Plant execution state
- Refresh cadence: daily
- Timestamp fields: email received time; `TODO` confirm whether message sent time is preferred
- Known risks / manual-edit concerns: subject line consistency matters; multiple same-day emails may reflect revisions or partial updates
- Precedence notes: first-pass source for `current_execution_state`; not intended as a universal winner for blends-specific or solids-specific execution domains
- Open questions / TODOs: confirm mailbox folder scope details; confirm whether latest-per-day should use sent time or received time

### Blends Shift Instructions

- Source id: `blends_shift_instructions`
- Location/path or mailbox/subject pattern: mailbox scope `Blends Operations`; subject contains `Blends Shift Instructions`
- Business purpose: blends execution guidance and same-day operating context
- Source category: Email
- Candidate classification: `authoritative`
- Selection rules: latest matching message per day
- Likely authoritative fields: blends execution state
- Refresh cadence: daily
- Timestamp fields: email received time; `TODO` confirm whether message sent time is preferred
- Known risks / manual-edit concerns: subject line consistency matters; blends-specific updates may conflict with broader North Plant instructions
- Precedence notes: first-pass source for `blends_execution_state`
- Open questions / TODOs: confirm mailbox folder scope details; confirm whether any blended domain exceptions exist

### K9/195 Evening News

- Source id: `k9_195_evening_news`
- Location/path or mailbox/subject pattern: mailbox scope `K9 / Solids Operations`; subject contains `K9/195 Evening News`
- Business purpose: solids execution guidance and same-day operating context
- Source category: Email
- Candidate classification: `authoritative`
- Selection rules: latest matching message per day; explicitly highest precedence for solids in the approved manifest
- Likely authoritative fields: solids execution state
- Refresh cadence: daily
- Timestamp fields: email received time; `TODO` confirm whether message sent time is preferred
- Known risks / manual-edit concerns: subject line consistency matters; later evening updates may materially change same-day interpretation
- Precedence notes: highest first-pass source for `solids_execution_state`
- Open questions / TODOs: confirm mailbox folder scope details; confirm whether any additional solids-specific corroborating source is needed in V1

## Explicit Exclusions

- Exclude SharePoint path `Morgantown/Operations/South Plant`
- Exclude filenames containing `South Plant`
- Exclude filenames or folders containing `Archive`

## Notes For Config Preparation

Use this document as the human-readable source of truth for `config/sources.yaml`.

Before changing source config, confirm:

- source identifiers stay stable
- path or mailbox selection rules still match the approved manifest
- tabs or sheets in scope are documented once they are known
- timestamp strategy is explicit and not inferred solely from file modified time
