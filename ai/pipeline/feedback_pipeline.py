"""
ai/pipeline/feedback_pipeline.py
===================================
Batch pipeline: loads the raw CSV (Kaggle dataset OR the small sample
file), cleans it using preprocessing/cleaning.py, and writes:
    - data/processed/cleaned_feedback.csv
    - data/processed/data_quality_report.json

This is a DEVELOPMENT/OFFLINE tool for preparing a dataset. It is NOT
what the backend calls at request-time — for that, see
services/feedback_analyzer.py, which processes one record at a time
with no file I/O.

HOW TO RUN
-----------
From inside the `ai/` folder:
    python -m pipeline.feedback_pipeline [--sample]

    --sample   use the small bundled sample_feedback.csv instead of
               the full Kaggle CSV (useful before you've downloaded
               the real dataset, or for a fast demo).
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from ai.config.config import (  # noqa: E402
    RAW_CSV_PATH,
    SAMPLE_CSV_PATH,
    CLEANED_CSV_PATH,
    QUALITY_REPORT_PATH,
    COLUMN_MAP,
    USEFUL_COLUMNS,
    CORE_TEXT_FIELDS,
    MIN_DESCRIPTION_LENGTH,
)
from ai.preprocessing.cleaning import (  # noqa: E402
    clean_text,
    is_text_usable,
    find_exact_duplicates,
    find_description_duplicates,
    missing_value_report,
    drop_rows_missing_core_text,
    fill_non_critical_missing,
)
from ai.schemas.feedback import empty_ai_analysis_dict  # noqa: E402

logger = logging.getLogger("ai.pipeline.feedback_pipeline")

# Toggle: also drop rows whose description text repeats an earlier
# row's (see cleaning.find_description_duplicates docstring).
DEDUPLICATE_ON_DESCRIPTION = True


def load_raw_data(path: Path) -> pd.DataFrame:
    """Load the CSV and rename columns to our normalized schema."""
    if not path.exists():
        raise FileNotFoundError(
            f"Could not find a dataset at {path}.\n"
            "Either download customer_support_tickets.csv from Kaggle into "
            "ai/data/raw/, or run with --sample to use the bundled sample "
            "file. See ai/README.md 'How to place the dataset'."
        )

    df = pd.read_csv(path)

    rename_map = {k: v for k, v in COLUMN_MAP.items() if k in df.columns}
    df = df.rename(columns=rename_map)

    unmatched = [c for c in df.columns if c not in COLUMN_MAP.values()]
    if unmatched:
        logger.info("Columns not in COLUMN_MAP (left as-is): %s", unmatched)

    return df


def select_useful_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Keep only the normalized columns our schema cares about."""
    available = [c for c in USEFUL_COLUMNS if c in df.columns]
    missing = [c for c in USEFUL_COLUMNS if c not in df.columns]
    if missing:
        logger.warning(
            "Expected columns not found in this file, skipping: %s. "
            "Check ai/config/config.py COLUMN_MAP against your actual CSV.",
            missing,
        )
    return df[available].copy()


def add_ai_analysis_placeholder(df: pd.DataFrame) -> pd.DataFrame:
    """Add empty AI fields — never fabricated, always None in Milestone 1."""
    df = df.copy()
    for field_name in empty_ai_analysis_dict():
        df[field_name] = None
    return df


def add_source_field(df: pd.DataFrame, source: str = "support_ticket") -> pd.DataFrame:
    """Every record from this pipeline came from the same dataset type."""
    df = df.copy()
    df["source"] = source
    return df


def run_pipeline(raw_path: Path) -> dict:
    """Run the full cleaning pipeline and return a stats dict."""
    stats: dict = {}

    df = load_raw_data(raw_path)
    stats["original_records"] = int(len(df))
    stats["original_columns"] = list(df.columns)
    logger.info("Loaded %d records from %s", len(df), raw_path)

    before_missing = missing_value_report(df)
    stats["missing_values_before"] = before_missing.to_dict(orient="records")

    df = select_useful_columns(df)

    for field_name in CORE_TEXT_FIELDS:
        if field_name in df.columns:
            df[field_name] = df[field_name].apply(clean_text)

    rows_before = len(df)
    if all(f in df.columns for f in CORE_TEXT_FIELDS):
        df = drop_rows_missing_core_text(df, CORE_TEXT_FIELDS)
    invalid_removed = rows_before - len(df)

    if "description" in df.columns:
        rows_before_len_check = len(df)
        usable_mask = df["description"].apply(lambda t: is_text_usable(t, MIN_DESCRIPTION_LENGTH))
        df = df[usable_mask].copy()
        invalid_removed += rows_before_len_check - len(df)
    stats["invalid_or_unusable_removed"] = int(invalid_removed)
    logger.info("Removed %d invalid/unusable records", invalid_removed)

    rows_before = len(df)
    exact_dupe_mask = find_exact_duplicates(df)
    df = df[~exact_dupe_mask].copy()
    exact_dupes_removed = rows_before - len(df)

    desc_dupes_removed = 0
    if DEDUPLICATE_ON_DESCRIPTION and "description" in df.columns:
        rows_before = len(df)
        desc_dupe_mask = find_description_duplicates(df, "description")
        df = df[~desc_dupe_mask].copy()
        desc_dupes_removed = rows_before - len(df)

    stats["exact_duplicates_removed"] = int(exact_dupes_removed)
    stats["description_duplicates_removed"] = int(desc_dupes_removed)
    stats["duplicates_removed_total"] = int(exact_dupes_removed + desc_dupes_removed)
    logger.info(
        "Removed %d duplicate records (%d exact, %d duplicate descriptions)",
        exact_dupes_removed + desc_dupes_removed,
        exact_dupes_removed,
        desc_dupes_removed,
    )

    df = fill_non_critical_missing(df)
    df = add_source_field(df)
    df = add_ai_analysis_placeholder(df)

    after_missing = missing_value_report(df)
    stats["missing_values_after"] = after_missing.to_dict(orient="records")
    stats["final_records"] = int(len(df))
    stats["final_columns"] = list(df.columns)

    CLEANED_CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(CLEANED_CSV_PATH, index=False)

    QUALITY_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(QUALITY_REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)

    logger.info("Saved cleaned dataset to %s", CLEANED_CSV_PATH)
    logger.info("Saved quality report to %s", QUALITY_REPORT_PATH)
    return stats


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Clean the feedback dataset.")
    parser.add_argument(
        "--sample",
        action="store_true",
        help="Use the small bundled sample_feedback.csv instead of the full Kaggle CSV.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
    args = _parse_args()
    path = SAMPLE_CSV_PATH if args.sample else RAW_CSV_PATH
    result_stats = run_pipeline(path)

    print("\n===== DATA QUALITY REPORT (Milestone 1) =====")
    print(f"Original records          : {result_stats['original_records']}")
    print(f"Invalid/unusable removed  : {result_stats['invalid_or_unusable_removed']}")
    print(f"Exact duplicates removed  : {result_stats['exact_duplicates_removed']}")
    print(f"Description dupes removed : {result_stats['description_duplicates_removed']}")
    print(f"Final records             : {result_stats['final_records']}")
    print(f"\nCleaned CSV: {CLEANED_CSV_PATH}")
    print(f"Report JSON: {QUALITY_REPORT_PATH}")
    print("================================================\n")
