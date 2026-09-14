"""
ai/tests/test_feedback_analyzer.py
=====================================
Tests for the public interface (ai/services/feedback_analyzer.py) that
the backend teammate will call. These tests simulate how FastAPI would
call this function — no FastAPI, MongoDB, or network access needed.

Run from the repo root:
    pytest ai/tests/ -v
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from ai.services.feedback_analyzer import analyze_feedback  # noqa: E402


def test_analyze_feedback_processes_valid_text():
    result = analyze_feedback(text="Payment failed during checkout", feedback_id="123")
    assert result["status"] == "processed"
    assert result["feedback_id"] == "123"
    assert result["cleaned_text"] == "Payment failed during checkout"
    assert "error" not in result


def test_analyze_feedback_cleans_messy_whitespace():
    result = analyze_feedback(text="Payment   failed\n\nduring checkout ")
    assert result["cleaned_text"] == "Payment failed during checkout"


def test_analyze_feedback_rejects_empty_string():
    result = analyze_feedback(text="")
    assert result["status"] == "rejected"
    assert "error" in result


def test_analyze_feedback_rejects_none():
    result = analyze_feedback(text=None)
    assert result["status"] == "rejected"


def test_analyze_feedback_rejects_wrong_type():
    result = analyze_feedback(text=12345)
    assert result["status"] == "rejected"


def test_analyze_feedback_rejects_too_short_text():
    result = analyze_feedback(text="na")
    assert result["status"] == "rejected"
    assert "error" in result


def test_analyze_feedback_echoes_feedback_id_even_on_rejection():
    result = analyze_feedback(text="", feedback_id="abc-999")
    assert result["feedback_id"] == "abc-999"


def test_analyze_feedback_never_raises_on_bad_input():
    # This is the core promise to the backend: bad input never crashes
    # the caller, it always comes back as a dict.
    for bad_input in [None, "", "   ", 42, [], {}]:
        result = analyze_feedback(text=bad_input)
        assert isinstance(result, dict)
        assert result["status"] == "rejected"


def test_analyze_feedback_output_is_json_serializable():
    import json

    result = analyze_feedback(text="Payment failed during checkout", feedback_id="123")
    json.dumps(result)  # raises if not serializable
