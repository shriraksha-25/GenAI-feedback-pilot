"""
ai/analysis/dataset_analysis.py
==================================
Look-only inspection of the raw CSV. Changes nothing. Run this FIRST,
before the pipeline, to confirm the real column names in your
downloaded file match ai/config/config.py's COLUMN_MAP.

HOW TO RUN
-----------
From the REPO ROOT (so the `ai` package is importable):
    python -m ai.analysis.dataset_analysis [--sample]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from ai.config.config import RAW_CSV_PATH, SAMPLE_CSV_PATH, USEFUL_COLUMNS  # noqa: E402
from ai.preprocessing.cleaning import missing_value_report  # noqa: E402


def inspect_dataset(path: Path) -> None:
    if not path.exists():
        print(f"[error] No file found at {path}")
        print("Place customer_support_tickets.csv in ai/data/raw/, or pass --sample.")
        return

    df = pd.read_csv(path)

    print("\n===== BASIC SHAPE =====")
    print(f"Rows   : {df.shape[0]}")
    print(f"Columns: {df.shape[1]}")

    print("\n===== COLUMN NAMES (as found in YOUR file) =====")
    for col in df.columns:
        print(f" - {col}")

    print("\n===== DATA TYPES =====")
    print(df.dtypes)

    print("\n===== MISSING VALUES PER COLUMN =====")
    print(missing_value_report(df).to_string(index=False))

    print("\n===== DUPLICATE ROWS =====")
    print(f"Exact duplicate rows: {int(df.duplicated().sum())}")

    print("\n===== SAMPLE RECORDS =====")
    print(df.head(3).to_string())

    print("\n===== BASIC STATISTICS (numeric columns) =====")
    numeric_df = df.select_dtypes(include="number")
    print(numeric_df.describe().to_string() if not numeric_df.empty else "No numeric columns found.")

    print("\n===== NORMALIZED SCHEMA WE KEEP FOR THE AI PIPELINE =====")
    for col in USEFUL_COLUMNS:
        print(f" - {col}")
    print(
        "\nIdentity fields (raw customer name/email) are intentionally "
        "excluded — the AI pipeline needs what the feedback is ABOUT, "
        "not who sent it.\n"
    )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspect the raw feedback dataset.")
    parser.add_argument("--sample", action="store_true", help="Inspect the bundled sample file instead.")
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    inspect_dataset(SAMPLE_CSV_PATH if args.sample else RAW_CSV_PATH)
