from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from morgantown_ops_hub.config_loader import load_config_bundle
from morgantown_ops_hub.config_models import Exclusions, SelectionRules, SourceDefinition
from morgantown_ops_hub.source_resolution import (
    SourceCandidateMetadata,
    load_candidate_fixture,
    resolve_candidates,
)


UTC = timezone.utc
REPO_ROOT = Path(__file__).resolve().parents[1]


def _timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value).astimezone(UTC)


def _workbook_source(
    *,
    source_id: str = "liquids_schedule",
    rules: SelectionRules | None = None,
) -> SourceDefinition:
    return SourceDefinition(
        source_id=source_id,
        source_name="Workbook Source",
        source_type="sharepoint_workbook",
        site_scope="Morgantown",
        plant_scope="North Plant",
        domain="planned_schedule",
        path=Path("Schedules/Workbook.xlsm"),
        selection_rules=rules or SelectionRules(latest_only=True),
        enabled=True,
        authoritative_for=["planned_schedule"],
        expected_refresh="daily",
        timestamp_strategy="business_timestamp",
    )


def _email_source(
    *,
    source_id: str = "north_plant_shift_instructions",
    rules: SelectionRules | None = None,
) -> SourceDefinition:
    return SourceDefinition(
        source_id=source_id,
        source_name="Shift Instructions",
        source_type="email",
        site_scope="Morgantown",
        plant_scope="North Plant",
        domain="current_execution_state",
        mailbox_scope="Operations",
        subject_patterns=["North Plant Shift Instructions"],
        selection_rules=rules or SelectionRules(latest_per_day=True),
        enabled=True,
        authoritative_for=["current_execution_state"],
        expected_refresh="daily",
        timestamp_strategy="email_received_time",
    )


def _candidate(
    *,
    source_id: str,
    candidate_name: str,
    source_type: str,
    candidate_path: str | None = None,
    folder_path: str | None = None,
    modified_at: str | None = None,
    business_timestamp: str | None = None,
    received_at: str | None = None,
    subject: str | None = None,
    extension: str | None = None,
) -> SourceCandidateMetadata:
    return SourceCandidateMetadata(
        source_id=source_id,
        candidate_name=candidate_name,
        candidate_path=Path(candidate_path) if candidate_path else None,
        source_type=source_type,
        folder_path=Path(folder_path) if folder_path else None,
        modified_at=_timestamp(modified_at) if modified_at else None,
        business_timestamp=_timestamp(business_timestamp) if business_timestamp else None,
        received_at=_timestamp(received_at) if received_at else None,
        subject=subject,
        extension=extension,
    )


def _resolve(source: SourceDefinition, candidates: list[SourceCandidateMetadata], exclusions: Exclusions | None = None):
    return resolve_candidates(
        [source],
        exclusions or Exclusions(),
        candidates,
        generated_at=_timestamp("2026-04-17T12:00:00+00:00"),
        site="Morgantown",
        plant_scope="North Plant",
    ).records[0]


def test_archive_exclusion_works() -> None:
    source = _workbook_source()
    exclusions = Exclusions(filename_contains=["Archive"])
    candidates = [
        _candidate(
            source_id=source.source_id,
            candidate_name="Master North Plant Liquids Schedule.xlsm",
            candidate_path="Morgantown/Operations/Schedules/Master North Plant Liquids Schedule.xlsm",
            folder_path="Morgantown/Operations/Schedules",
            source_type="sharepoint_workbook",
            modified_at="2026-04-17T13:00:00+00:00",
            business_timestamp="2026-04-17T12:00:00+00:00",
            extension=".xlsm",
        ),
        _candidate(
            source_id=source.source_id,
            candidate_name="Master North Plant Liquids Schedule Archive.xlsm",
            candidate_path="Morgantown/Operations/Schedules/Archive/Master North Plant Liquids Schedule Archive.xlsm",
            folder_path="Morgantown/Operations/Schedules/Archive",
            source_type="sharepoint_workbook",
            modified_at="2026-04-18T13:00:00+00:00",
            business_timestamp="2026-04-18T12:00:00+00:00",
            extension=".xlsm",
        ),
    ]

    record = _resolve(source, candidates, exclusions)

    assert [candidate.candidate_name for candidate in record.selected_candidates] == [
        "Master North Plant Liquids Schedule.xlsm"
    ]
    assert record.excluded_candidates[0].reasons == ["Excluded by manifest filename_contains rule: Archive"]


def test_south_plant_exclusion_works_when_path_contains_it() -> None:
    source = _workbook_source()
    exclusions = Exclusions(
        sharepoint_paths=["Morgantown/Operations/South Plant"],
        filename_contains=["South Plant"],
    )
    candidates = [
        _candidate(
            source_id=source.source_id,
            candidate_name="Master South Plant Liquids Schedule.xlsm",
            candidate_path="Morgantown/Operations/South Plant/Master South Plant Liquids Schedule.xlsm",
            folder_path="Morgantown/Operations/South Plant",
            source_type="sharepoint_workbook",
            modified_at="2026-04-17T13:00:00+00:00",
            business_timestamp="2026-04-17T12:00:00+00:00",
            extension=".xlsm",
        )
    ]

    record = _resolve(source, candidates, exclusions)

    assert record.selected_candidates == []
    assert len(record.excluded_candidates) == 1
    assert "sharepoint_paths" in record.excluded_candidates[0].reasons[0]


def test_latest_only_selects_newest_eligible_candidate() -> None:
    source = _workbook_source(rules=SelectionRules(latest_only=True))
    candidates = [
        _candidate(
            source_id=source.source_id,
            candidate_name="Older Workbook.xlsm",
            candidate_path="Schedules/Older Workbook.xlsm",
            folder_path="Schedules",
            source_type="sharepoint_workbook",
            modified_at="2026-04-16T13:00:00+00:00",
            business_timestamp="2026-04-16T12:00:00+00:00",
            extension=".xlsm",
        ),
        _candidate(
            source_id=source.source_id,
            candidate_name="Newest Workbook.xlsm",
            candidate_path="Schedules/Newest Workbook.xlsm",
            folder_path="Schedules",
            source_type="sharepoint_workbook",
            modified_at="2026-04-17T13:00:00+00:00",
            business_timestamp="2026-04-17T12:00:00+00:00",
            extension=".xlsm",
        ),
    ]

    record = _resolve(source, candidates)

    assert [candidate.candidate_name for candidate in record.selected_candidates] == ["Newest Workbook.xlsm"]


def test_latest_n_selects_newest_n_eligible_candidates() -> None:
    source = _workbook_source(source_id="shipping_dated_schedules", rules=SelectionRules(latest_n=2))
    candidates = [
        _candidate(
            source_id=source.source_id,
            candidate_name="20260415 Schedule.xlsm",
            candidate_path="Shipping/20260415 Schedule.xlsm",
            folder_path="Shipping",
            source_type="sharepoint_workbook",
            modified_at="2026-04-15T10:00:00+00:00",
            business_timestamp="2026-04-15T08:00:00+00:00",
            extension=".xlsm",
        ),
        _candidate(
            source_id=source.source_id,
            candidate_name="20260416 Schedule.xlsm",
            candidate_path="Shipping/20260416 Schedule.xlsm",
            folder_path="Shipping",
            source_type="sharepoint_workbook",
            modified_at="2026-04-16T10:00:00+00:00",
            business_timestamp="2026-04-16T08:00:00+00:00",
            extension=".xlsm",
        ),
        _candidate(
            source_id=source.source_id,
            candidate_name="20260417 Schedule.xlsm",
            candidate_path="Shipping/20260417 Schedule.xlsm",
            folder_path="Shipping",
            source_type="sharepoint_workbook",
            modified_at="2026-04-17T10:00:00+00:00",
            business_timestamp="2026-04-17T08:00:00+00:00",
            extension=".xlsm",
        ),
    ]

    record = _resolve(source, candidates)

    assert [candidate.candidate_name for candidate in record.selected_candidates] == [
        "20260417 Schedule.xlsm",
        "20260416 Schedule.xlsm",
    ]


def test_prefer_extension_favors_xlsm_when_otherwise_tied() -> None:
    source = _workbook_source(rules=SelectionRules(latest_only=True, prefer_extension=".xlsm"))
    candidates = [
        _candidate(
            source_id=source.source_id,
            candidate_name="Master Solids Schedule.xlsx",
            candidate_path="Schedules/Master Solids Schedule.xlsx",
            folder_path="Schedules",
            source_type="sharepoint_workbook",
            modified_at="2026-04-17T10:00:00+00:00",
            business_timestamp="2026-04-17T08:00:00+00:00",
            extension=".xlsx",
        ),
        _candidate(
            source_id=source.source_id,
            candidate_name="Master Solids Schedule.xlsm",
            candidate_path="Schedules/Master Solids Schedule.xlsm",
            folder_path="Schedules",
            source_type="sharepoint_workbook",
            modified_at="2026-04-17T10:00:00+00:00",
            business_timestamp="2026-04-17T08:00:00+00:00",
            extension=".xlsm",
        ),
    ]

    record = _resolve(source, candidates)

    assert [candidate.candidate_name for candidate in record.selected_candidates] == ["Master Solids Schedule.xlsm"]
    assert "preferred extension .xlsm" in record.selected_candidates[0].reason


def test_latest_per_day_for_email_chooses_newest_message_per_day() -> None:
    source = _email_source()
    candidates = [
        _candidate(
            source_id=source.source_id,
            candidate_name="North Plant Shift Instructions - 2026-04-16 AM",
            candidate_path="mailbox/Operations/2026-04-16-0700.eml",
            folder_path="mailbox/Operations",
            source_type="email",
            received_at="2026-04-16T07:00:00+00:00",
            subject="North Plant Shift Instructions",
        ),
        _candidate(
            source_id=source.source_id,
            candidate_name="North Plant Shift Instructions - 2026-04-17 AM",
            candidate_path="mailbox/Operations/2026-04-17-0700.eml",
            folder_path="mailbox/Operations",
            source_type="email",
            received_at="2026-04-17T07:00:00+00:00",
            subject="North Plant Shift Instructions",
        ),
        _candidate(
            source_id=source.source_id,
            candidate_name="North Plant Shift Instructions - 2026-04-17 PM",
            candidate_path="mailbox/Operations/2026-04-17-1900.eml",
            folder_path="mailbox/Operations",
            source_type="email",
            received_at="2026-04-17T19:00:00+00:00",
            subject="North Plant Shift Instructions",
        ),
    ]

    record = _resolve(source, candidates)

    assert [candidate.candidate_name for candidate in record.selected_candidates] == [
        "North Plant Shift Instructions - 2026-04-17 PM",
        "North Plant Shift Instructions - 2026-04-16 AM",
    ]
    assert [candidate.selection_date.isoformat() for candidate in record.selected_candidates] == [
        "2026-04-17",
        "2026-04-16",
    ]


def test_sample_fixture_resolves_against_real_config() -> None:
    config_bundle = load_config_bundle(REPO_ROOT / "config")
    fixture = load_candidate_fixture(REPO_ROOT / "samples" / "source_candidates_fixture.json")

    report = resolve_candidates(
        config_bundle.manifest.sources,
        config_bundle.manifest.exclusions,
        fixture.candidates,
        generated_at=_timestamp("2026-04-17T12:00:00+00:00"),
        site=config_bundle.manifest.site,
        plant_scope=config_bundle.manifest.plant_scope,
        fixture_path=REPO_ROOT / "samples" / "source_candidates_fixture.json",
    )

    records_by_source = {record.source_id: record for record in report.records}

    assert [candidate.candidate_name for candidate in records_by_source["liquids_schedule"].selected_candidates] == [
        "Master North Plant Liquids Schedule.xlsm"
    ]
    assert [candidate.candidate_name for candidate in records_by_source["shipping_dated_schedules"].selected_candidates] == [
        "20260417 Schedule.xlsm",
        "20260416 Schedule.xlsm",
    ]
