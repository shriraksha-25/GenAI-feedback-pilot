"""
ai/tests/test_preprocessing.py
=================================
Tests for ai/preprocessing/cleaning.py. No file I/O, no MongoDB, no
FastAPI, no API keys required — pure function tests.

Run from the repo root:
    pytest ai/tests/ -v
"""

import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from ai.preprocessing.cleaning import (  # noqa: E402
    clean_text,
    is_text_usable,
    find_exact_duplicates,
    find_description_duplicates,
    drop_rows_missing_core_text,
    fill_non_critical_missing,
)


def test_clean_text_collapses_whitespace():
    messy = "Hi,\n\n   my app   keeps crashing!!\t\t"
    assert clean_text(messy) == "Hi, my app keeps crashing!!"


def test_clean_text_handles_missing_value():
    assert clean_text(float("nan")) == ""
    assert clean_text(None) == ""


def test_clean_text_handles_non_string_input():
    # A malformed record might hand us a number or a list by mistake.
    assert clean_text(12345) == "12345"


def test_clean_text_keeps_punctuation_and_case():
    assert clean_text("This is BROKEN!") == "This is BROKEN!"


def test_is_text_usable_rejects_short_junk():
    assert is_text_usable("na", min_length=15) is False
    assert is_text_usable("-", min_length=15) is False
    assert is_text_usable("", min_length=15) is False


def test_is_text_usable_accepts_real_complaint():
    assert is_text_usable("App keeps crashing on login.", min_length=15) is True


def test_find_exact_duplicates():
    df = pd.DataFrame({"feedback_id": [1, 2, 2, 3], "description": ["a", "b", "b", "c"]})
    assert list(find_exact_duplicates(df)) == [False, False, True, False]


def test_find_description_duplicates_different_ids():
    df = pd.DataFrame(
        {"feedback_id": [1, 2, 3], "description": ["App crashes", "App crashes", "Different issue"]}
    )
    assert list(find_description_duplicates(df, "description")) == [False, True, False]


def test_drop_rows_missing_core_text():
    df = pd.DataFrame(
        {
            "subject": ["Login issue", "", None],
            "description": ["", "Cannot reset password", ""],
        }
    )
    result = drop_rows_missing_core_text(df, ["subject", "description"])
    assert len(result) == 2


def test_fill_non_critical_missing():
    df = pd.DataFrame({"priority": ["High", None, "Low"]})
    result = fill_non_critical_missing(df)
    assert result["priority"].isna().sum() == 0
    assert result["priority"].iloc[1] == "Unknown"
