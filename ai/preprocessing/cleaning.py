"""
ai/preprocessing/cleaning.py
==============================
Small, single-purpose, independently testable cleaning functions.
Used by both the batch pipeline (pipeline/feedback_pipeline.py, for
cleaning a whole CSV) and the single-record service
(services/feedback_analyzer.py, for cleaning one piece of text at a
time coming from the backend). Keeping the logic here means both call
sites share exactly the same cleaning rules — there is no second
copy-pasted version anywhere.

This file has no dependency on file paths, MongoDB, or FastAPI. It
only takes pandas objects / plain strings in and returns pandas
objects / plain strings out, which is what makes it independently
testable (see tests/test_preprocessing.py) without any of the rest of
the system running.
"""

from __future__ import annotations

import re
from typing import Iterable

import pandas as pd


# ---------------------------------------------------------------------
# TEXT CLEANING
# ---------------------------------------------------------------------
def clean_text(text: object) -> str:
    """
    Normalize a single piece of free text WITHOUT destroying
    information an NLP model could use later.

    Handles missing/non-string input (None, NaN, numbers) safely by
    returning "" instead of raising — a malformed single record
    should never crash a batch of 8,000 others.

    What we do and why:
    - Collapse whitespace/newlines/tabs into single spaces.
    - Strip stray control characters (encoding artifacts).
    - Strip leading/trailing whitespace.

    What we deliberately do NOT do:
    - Lowercase everything (casing can signal frustration, e.g. ALL CAPS).
    - Remove punctuation or stopwords (needed by some future NLP
      techniques, e.g. transformers use them as context; sentiment
      cues like "!" and "?" would be lost).
    """
    if text is None:
        return ""
    try:
        if pd.isna(text):
            return ""
    except (TypeError, ValueError):
        # pd.isna() can raise on some non-scalar inputs; treat those
        # as "not missing" and fall through to str() conversion.
        pass

    text = str(text)
    text = re.sub(r"[\x00-\x1f\x7f]", " ", text)  # control chars -> space
    text = re.sub(r"\s+", " ", text)  # collapse whitespace
    return text.strip()


def is_text_usable(text: str, min_length: int) -> bool:
    """
    Decide whether cleaned text counts as real feedback vs. junk
    ("na", "-", "test", empty). Deliberately just a length check —
    see README for why we don't try to be cleverer here.
    """
    if not text:
        return False
    return len(text) >= min_length


# ---------------------------------------------------------------------
# DUPLICATE HANDLING
# ---------------------------------------------------------------------
def find_exact_duplicates(df: pd.DataFrame) -> pd.Series:
    """Boolean mask: True for rows that exactly repeat an earlier row."""
    return df.duplicated(keep="first")


def find_description_duplicates(df: pd.DataFrame, text_column: str) -> pd.Series:
    """
    Boolean mask: True for rows whose `text_column` repeats an earlier
    row's text even if other columns (id, date) differ — e.g. the same
    complaint submitted twice under different ticket IDs.
    """
    return df.duplicated(subset=[text_column], keep="first")


# ---------------------------------------------------------------------
# MISSING VALUE HANDLING
# ---------------------------------------------------------------------
def missing_value_report(df: pd.DataFrame) -> pd.DataFrame:
    """Per-column missing count/percent — used before AND after cleaning."""
    missing_count = df.isna().sum()
    missing_percent = (missing_count / len(df) * 100).round(2) if len(df) else missing_count
    report = pd.DataFrame(
        {
            "column": df.columns,
            "missing_count": missing_count.values,
            "missing_percent": missing_percent.values,
        }
    )
    return report.sort_values("missing_count", ascending=False).reset_index(drop=True)


def drop_rows_missing_core_text(df: pd.DataFrame, core_text_fields: Iterable[str]) -> pd.DataFrame:
    """
    Drop rows where ALL core text fields (e.g. subject AND description)
    are empty/missing. A row with at least one populated core text
    field is kept.
    """
    core_text_fields = list(core_text_fields)

    def _has_text(col: pd.Series) -> pd.Series:
        stripped = col.where(~col.isna(), "").astype(str).str.strip()
        return stripped != ""

    has_any_text = df[core_text_fields].apply(_has_text)
    keep_mask = has_any_text.any(axis=1)
    return df[keep_mask].copy()


def fill_non_critical_missing(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fill missing NON-text-content metadata (priority, channel, ...)
    with an explicit "Unknown" marker instead of dropping the row.
    Never used for core text fields — inventing feedback the customer
    never gave would be dishonest (handled separately, and never
    filled, only dropped-or-kept, in drop_rows_missing_core_text).
    """
    df = df.copy()
    text_like_cols = df.select_dtypes(include=["object", "str"]).columns
    for col in text_like_cols:
        df[col] = df[col].fillna("Unknown")
    return df
