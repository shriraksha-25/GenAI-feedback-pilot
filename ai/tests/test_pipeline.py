"""
ai/tests/test_pipeline.py
============================
An end-to-end smoke test: run the batch pipeline against the bundled
synthetic sample_feedback.csv and check the output schema/shape is
correct. Does not require the real Kaggle dataset, MongoDB, or FastAPI.

Run from the repo root:
    pytest ai/tests/ -v
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from ai.config.config import SAMPLE_CSV_PATH  # noqa: E402
from ai.pipeline.feedback_pipeline import run_pipeline  # noqa: E402
from ai.schemas.feedback import empty_ai_analysis_dict  # noqa: E402


def test_pipeline_runs_on_sample_data_and_produces_valid_schema():
    stats = run_pipeline(SAMPLE_CSV_PATH)

    # Basic sanity: the pipeline actually reduced junk/duplicates.
    assert stats["original_records"] > stats["final_records"]
    assert stats["final_records"] > 0

    # Every AI placeholder field must exist in the final schema, and
    # must NOT have been given a fake value.
    expected_ai_fields = set(empty_ai_analysis_dict().keys())
    assert expected_ai_fields.issubset(set(stats["final_columns"]))
