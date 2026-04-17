"""Normalization helpers for source columns, labels, and values."""

from __future__ import annotations

import re
from collections.abc import Iterable


_NON_ALNUM = re.compile(r"[^a-z0-9]+")


def normalize_column_name(name: str) -> str:
    """Convert a source column label into a stable snake_case key."""
    cleaned = name.strip().lower()
    cleaned = _NON_ALNUM.sub("_", cleaned)
    return cleaned.strip("_")


def normalize_headers(headers: Iterable[str]) -> list[str]:
    """Normalize a sequence of column headers."""
    return [normalize_column_name(header) for header in headers]


def normalize_text(value: str | None) -> str | None:
    """Collapse excess whitespace for a source text value."""
    if value is None:
        return None
    return " ".join(value.split())
