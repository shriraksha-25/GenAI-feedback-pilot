"""
ai/tests/test_context.py
===========================
Tests for ai/agents/context.py's format_context_block(). Pure string
formatting, no network, no API key, no crewai needed to run these.

Run from the repo root:
    pytest ai/tests/ -v
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from ai.agents.context import format_context_block  # noqa: E402


def test_empty_context_shows_explicit_none_provided_for_every_section():
    text = format_context_block({})
    assert "(not provided)" in text or "(none provided)" in text
    assert "Themes" in text
    assert "Customer pain points" in text
    assert "Feature requests" in text
    assert "Supporting evidence" in text


def test_none_context_does_not_crash():
    text = format_context_block(None)
    assert "Feature name: (not provided)" in text


def test_rich_context_includes_all_supplied_values():
    context = {
        "feature_name": "Save frequently used reports",
        "themes": ["Reporting"],
        "pain_points": ["Regenerating the same report every time is tedious."],
        "feature_requests": ["Save frequently used reports"],
        "feature_opportunity_group": "Reporting Improvements",
        "supporting_evidence": [{"feedback_id": "42", "text": "I wish I could save my reports."}],
    }
    text = format_context_block(context)
    assert "Save frequently used reports" in text
    assert "Reporting" in text
    assert "Regenerating the same report" in text
    assert "feedback_id=42" in text
    assert "I wish I could save my reports." in text
    assert "Reporting Improvements" in text


def test_priority_info_included_when_present():
    context = {"priority": {"score": 8.4, "reach": 1000, "impact": 2, "confidence": 0.8, "effort": 3, "reasoning": "high impact"}}
    text = format_context_block(context)
    assert "score=8.4" in text
    assert "reach=1000" in text


def test_priority_info_explicitly_absent_when_not_present():
    text = format_context_block({})
    assert "Priority information: (none provided)" in text


def test_previous_prd_summary_included_when_present():
    context = {"prd": {"title": "Existing PRD Title", "risks": ["risk A"], "dependencies": ["dep A"]}}
    text = format_context_block(context)
    assert "Previously generated PRD available: yes" in text
    assert "Existing PRD Title" in text
    assert "risk A" in text


def test_previous_prd_absent_by_default():
    text = format_context_block({})
    assert "Previously generated PRD available: no" in text
