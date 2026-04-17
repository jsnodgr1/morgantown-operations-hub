"""Local-only source candidate resolution for the V1 scaffold."""

from __future__ import annotations

import json
import re
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, ValidationError, computed_field

from morgantown_ops_hub.config_models import Exclusions, SelectionRules, SourceDefinition, SourceType


class ResolutionError(ValueError):
    """Raised when candidate fixtures or selection rules cannot be resolved."""


class ResolutionBaseModel(BaseModel):
    """Strict base model for resolution data."""

    model_config = ConfigDict(extra="forbid")


class SourceCandidateMetadata(ResolutionBaseModel):
    """Local metadata for a potential source candidate."""

    source_id: str
    candidate_name: str
    candidate_path: Path | None = None
    source_type: SourceType
    modified_at: datetime | None = None
    business_timestamp: datetime | None = None
    received_at: datetime | None = None
    folder_path: Path | None = None
    subject: str | None = None
    extension: str | None = None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def normalized_extension(self) -> str | None:
        """Return a normalized lower-case extension for comparisons."""
        if self.extension:
            return self.extension.lower()
        if self.candidate_path is not None:
            suffix = self.candidate_path.suffix
            return suffix.lower() or None
        return None


class ExcludedCandidateRecord(ResolutionBaseModel):
    """Trace record for a rejected candidate."""

    candidate_name: str
    candidate_path: Path | None = None
    reasons: list[str] = Field(default_factory=list)


class SelectedCandidateRecord(ResolutionBaseModel):
    """Trace record for a winning candidate."""

    candidate_name: str
    candidate_path: Path | None = None
    source_type: SourceType
    modified_at: datetime | None = None
    business_timestamp: datetime | None = None
    received_at: datetime | None = None
    selected_timestamp: datetime | None = None
    selection_date: date | None = None
    reason: str


class SelectedSourceRecord(ResolutionBaseModel):
    """Resolution result for a single configured source."""

    source_id: str
    source_name: str
    source_type: SourceType
    enabled: bool
    selection_mode: str
    trace: list[str] = Field(default_factory=list)
    selected_candidates: list[SelectedCandidateRecord] = Field(default_factory=list)
    excluded_candidates: list[ExcludedCandidateRecord] = Field(default_factory=list)


class SourceResolutionReport(ResolutionBaseModel):
    """Deterministic source-resolution artifact."""

    site: str
    plant_scope: str
    generated_at: datetime
    fixture_path: Path | None = None
    records: list[SelectedSourceRecord]


class SourceCandidateFixture(ResolutionBaseModel):
    """JSON fixture payload for local dry-run source resolution."""

    candidates: list[SourceCandidateMetadata]


def load_candidate_fixture(path: Path) -> SourceCandidateFixture:
    """Load and validate a local JSON candidate fixture."""
    try:
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except FileNotFoundError as exc:
        raise ResolutionError(f"Candidate fixture not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ResolutionError(f"Invalid JSON in candidate fixture {path}: {exc}") from exc

    if isinstance(payload, list):
        payload = {"candidates": payload}
    if not isinstance(payload, dict):
        raise ResolutionError(f"Expected a JSON object or list in candidate fixture {path}.")

    try:
        return SourceCandidateFixture.model_validate(payload)
    except ValidationError as exc:
        raise ResolutionError(f"Invalid candidate fixture {path}: {exc}") from exc


def resolve_candidates(
    sources: list[SourceDefinition],
    exclusions: Exclusions,
    candidates: list[SourceCandidateMetadata],
    *,
    generated_at: datetime,
    site: str,
    plant_scope: str,
    fixture_path: Path | None = None,
) -> SourceResolutionReport:
    """Resolve local candidate metadata into selected source candidates."""
    known_source_ids = {source.source_id for source in sources}
    unknown_candidate_sources = sorted({candidate.source_id for candidate in candidates if candidate.source_id not in known_source_ids})
    if unknown_candidate_sources:
        joined = ", ".join(unknown_candidate_sources)
        raise ResolutionError(f"Candidate fixture references unknown source_id values: {joined}")

    candidates_by_source: dict[str, list[SourceCandidateMetadata]] = defaultdict(list)
    for candidate in candidates:
        candidates_by_source[candidate.source_id].append(candidate)

    records = [
        _resolve_source(source, exclusions, candidates_by_source.get(source.source_id, []))
        for source in sources
    ]
    return SourceResolutionReport(
        site=site,
        plant_scope=plant_scope,
        generated_at=generated_at,
        fixture_path=fixture_path,
        records=records,
    )


def _resolve_source(
    source: SourceDefinition,
    exclusions: Exclusions,
    candidates: list[SourceCandidateMetadata],
) -> SelectedSourceRecord:
    """Resolve candidates for one configured source."""
    selection_mode = _selection_mode_name(source.selection_rules)
    record = SelectedSourceRecord(
        source_id=source.source_id,
        source_name=source.source_name,
        source_type=source.source_type,
        enabled=source.enabled,
        selection_mode=selection_mode,
    )

    if not source.enabled:
        record.trace.append("Source disabled in manifest; no candidates evaluated.")
        record.excluded_candidates.extend(
            ExcludedCandidateRecord(
                candidate_name=candidate.candidate_name,
                candidate_path=candidate.candidate_path,
                reasons=["Source disabled in manifest."],
            )
            for candidate in candidates
        )
        return record

    eligible: list[SourceCandidateMetadata] = []
    for candidate in candidates:
        reasons = _evaluate_candidate(source, exclusions, candidate)
        if reasons:
            record.excluded_candidates.append(
                ExcludedCandidateRecord(
                    candidate_name=candidate.candidate_name,
                    candidate_path=candidate.candidate_path,
                    reasons=reasons,
                )
            )
        else:
            eligible.append(candidate)

    if source.selection_rules.highest_precedence_for_solids:
        record.trace.append(
            "Selection rule highest_precedence_for_solids is recorded for cross-source precedence handling."
        )

    if not eligible:
        record.trace.append("No eligible candidates remained after exclusions and filters.")
        return record

    selected = _select_candidates(source, eligible)
    record.selected_candidates = [
        SelectedCandidateRecord(
            candidate_name=candidate.candidate_name,
            candidate_path=candidate.candidate_path,
            source_type=candidate.source_type,
            modified_at=candidate.modified_at,
            business_timestamp=candidate.business_timestamp,
            received_at=candidate.received_at,
            selected_timestamp=_selection_timestamp(source, candidate),
            selection_date=_selection_date(source, candidate),
            reason=reason,
        )
        for candidate, reason in selected
    ]
    record.trace.append(
        f"Evaluated {len(candidates)} candidates, kept {len(eligible)}, selected {len(record.selected_candidates)}."
    )
    return record


def _evaluate_candidate(
    source: SourceDefinition,
    exclusions: Exclusions,
    candidate: SourceCandidateMetadata,
) -> list[str]:
    """Return exclusion reasons for a candidate, if any."""
    reasons: list[str] = []
    if candidate.source_type != source.source_type:
        reasons.append(
            f"Candidate source_type {candidate.source_type.value} does not match configured source_type {source.source_type.value}."
        )

    for value in exclusions.sharepoint_paths:
        if _matches_path_fragment(candidate, value):
            reasons.append(f"Excluded by manifest sharepoint_paths rule: {value}")

    for value in exclusions.filename_contains:
        if _matches_text_fragment(candidate, value):
            reasons.append(f"Excluded by manifest filename_contains rule: {value}")

    rules = source.selection_rules

    for value in rules.exclude_name_contains:
        if _matches_text_fragment(candidate, value):
            reasons.append(f"Excluded by selection_rules.exclude_name_contains: {value}")

    for value in rules.exclude_folders:
        if _matches_folder_fragment(candidate, value):
            reasons.append(f"Excluded by selection_rules.exclude_folders: {value}")

    if rules.filename_pattern is not None:
        if re.search(rules.filename_pattern, candidate.candidate_name) is None:
            reasons.append(f"Excluded by selection_rules.filename_pattern: {rules.filename_pattern}")

    if rules.scope is not None:
        if not _matches_scope(candidate, rules.scope):
            reasons.append(f"Excluded by selection_rules.scope: {rules.scope}")

    return reasons


def _select_candidates(
    source: SourceDefinition,
    candidates: list[SourceCandidateMetadata],
) -> list[tuple[SourceCandidateMetadata, str]]:
    """Apply the primary selection mode to eligible candidates."""
    rules = source.selection_rules
    ranked = sorted(candidates, key=lambda candidate: _ranking_key(source, candidate))

    if rules.latest_only:
        winner = ranked[0]
        reason = f"Selected newest eligible candidate by {_timestamp_label(source)}."
        if rules.prefer_extension and winner.normalized_extension == rules.prefer_extension:
            reason += f" Tie broken in favor of preferred extension {rules.prefer_extension}."
        return [(winner, reason)]

    if rules.latest_n is not None:
        winners = ranked[: rules.latest_n]
        return [
            (
                candidate,
                f"Selected among the newest {rules.latest_n} eligible candidates by {_timestamp_label(source)}.",
            )
            for candidate in winners
        ]

    if rules.latest_per_day:
        winners: list[tuple[SourceCandidateMetadata, str]] = []
        seen_days: set[date] = set()
        for candidate in ranked:
            selection_date = _selection_date(source, candidate)
            if selection_date is None or selection_date in seen_days:
                continue
            seen_days.add(selection_date)
            winners.append(
                (
                    candidate,
                    f"Selected newest eligible candidate for {selection_date.isoformat()} by {_timestamp_label(source)}.",
                )
            )
        return winners

    return [(candidate, "Selected because no primary selection mode was configured.") for candidate in ranked]


def _selection_mode_name(rules: SelectionRules) -> str:
    """Return the configured primary selection mode."""
    if rules.latest_only:
        return "latest_only"
    if rules.latest_n is not None:
        return "latest_n"
    if rules.latest_per_day:
        return "latest_per_day"
    return "all_eligible"


def _selection_timestamp(source: SourceDefinition, candidate: SourceCandidateMetadata) -> datetime | None:
    """Choose the timestamp used for source selection."""
    if source.source_type == SourceType.EMAIL:
        if source.selection_rules.latest_per_day:
            return candidate.business_timestamp or candidate.received_at or candidate.modified_at
        return candidate.business_timestamp or candidate.received_at or candidate.modified_at
    return candidate.business_timestamp or candidate.modified_at or candidate.received_at


def _selection_date(source: SourceDefinition, candidate: SourceCandidateMetadata) -> date | None:
    """Return the date used for latest_per_day grouping."""
    timestamp = _selection_timestamp(source, candidate)
    return timestamp.date() if timestamp is not None else None


def _ranking_key(source: SourceDefinition, candidate: SourceCandidateMetadata) -> tuple[float, int, str, str]:
    """Return a deterministic sort key where the smallest tuple is the best candidate."""
    timestamp = _selection_timestamp(source, candidate)
    timestamp_score = -timestamp.timestamp() if timestamp is not None else float("inf")
    rules = source.selection_rules
    extension_bonus = 0
    if rules.prefer_extension and candidate.normalized_extension == rules.prefer_extension:
        extension_bonus = -1
    path_text = _normalize_text(candidate.candidate_path)
    return (timestamp_score, extension_bonus, path_text, candidate.candidate_name.lower())


def _timestamp_label(source: SourceDefinition) -> str:
    """Describe the timestamp strategy used for ordering."""
    if source.source_type == SourceType.EMAIL and source.selection_rules.latest_per_day:
        return "business_timestamp, then received_at"
    if source.source_type == SourceType.EMAIL:
        return "business_timestamp, then received_at"
    return "business_timestamp, then modified_at"


def _matches_scope(candidate: SourceCandidateMetadata, scope: str) -> bool:
    """Check whether the candidate metadata reflects the configured scope."""
    normalized_scope = scope.lower()
    haystacks = [
        candidate.candidate_name.lower(),
        _normalize_text(candidate.candidate_path),
        _normalize_text(candidate.folder_path),
        (candidate.subject or "").lower(),
    ]
    return any(normalized_scope in haystack for haystack in haystacks)


def _matches_path_fragment(candidate: SourceCandidateMetadata, fragment: str) -> bool:
    """Check whether a path-like fragment appears in path metadata."""
    normalized_fragment = _normalize_fragment(fragment)
    return any(
        normalized_fragment in haystack
        for haystack in (
            _normalize_text(candidate.candidate_path),
            _normalize_text(candidate.folder_path),
        )
    )


def _matches_folder_fragment(candidate: SourceCandidateMetadata, fragment: str) -> bool:
    """Check whether a folder exclusion matches the candidate folder or path."""
    normalized_fragment = _normalize_fragment(fragment)
    return any(
        normalized_fragment in haystack
        for haystack in (
            _normalize_text(candidate.folder_path),
            _normalize_text(candidate.candidate_path),
        )
    )


def _matches_text_fragment(candidate: SourceCandidateMetadata, fragment: str) -> bool:
    """Check whether a text fragment appears in candidate name, path, or subject."""
    normalized_fragment = fragment.lower()
    haystacks = [
        candidate.candidate_name.lower(),
        _normalize_text(candidate.candidate_path),
        _normalize_text(candidate.folder_path),
        (candidate.subject or "").lower(),
    ]
    return any(normalized_fragment in haystack for haystack in haystacks)


def _normalize_fragment(value: str) -> str:
    """Normalize a path fragment for cross-platform substring matching."""
    return value.replace("\\", "/").lower()


def _normalize_text(value: Path | None) -> str:
    """Normalize a path-like value for case-insensitive matching."""
    if value is None:
        return ""
    return str(value).replace("\\", "/").lower()
