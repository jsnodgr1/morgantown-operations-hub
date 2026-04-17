"""Excel IO helpers for local workbook ingestion."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def read_workbook_sheet(path: Path, sheet_name: str) -> pd.DataFrame:
    """Read a single Excel sheet into a DataFrame."""
    return pd.read_excel(path, sheet_name=sheet_name, engine="openpyxl")
