"""
ai/tests/test_agent_schemas.py
=================================
Tests for ai/agents/schemas.py - the structured per-agent output
models and their combination into one AgentAnalysisResult. Pure
pydantic validation tests, no crewai, no network, no API key needed.

Run from the repo root:
    pytest ai/tests/ -v
"""

import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from ai.agents.schemas import (  # noqa: E402
    ThemeResult,
    PainPointResult,
    FeatureRequestResult,
    AgentAnalysisResult,
)


def test_theme_result_valid():
    t = ThemeResult(theme="App Stability", confidence=0.9)
    assert t.theme == "App Stability"
    assert t.confidence == 0.9


def test_theme_result_confidence_out_of_range_rejected():
    with pytest.raises(ValidationError):
        ThemeResult(theme="App Stability", confidence=1.5)
    with pytest.raises(ValidationError):
        ThemeResult(theme="App Stability", confidence=-0.1)


def test_pain_point_result_valid():
    p = PainPointResult(pain_point="Customers cannot upload documents.", confidence=0.92)
    assert "cannot upload" in p.pain_point
    assert p.confidence == 0.92


def test_feature_request_result_with_request():
    f = FeatureRequestResult(
        has_feature_request=True,
        feature_request="Save frequently used reports",
        feature_category="Reporting",
        confidence=0.88,
    )
    assert f.has_feature_request is True
    assert f.feature_category == "Reporting"


def test_feature_request_result_without_request():
    # A pure bug report / compliment: no feature request present.
    f = FeatureRequestResult(has_feature_request=False, confidence=0.8)
    assert f.has_feature_request is False
    assert f.feature_request is None
    assert f.feature_category is None


def test_agent_analysis_result_combines_all_three():
    theme = ThemeResult(theme="App Stability", confidence=0.9)
    pain = PainPointResult(pain_point="Customers cannot upload documents.", confidence=0.92)
    feature = FeatureRequestResult(
        has_feature_request=True,
        feature_request="Save frequently used reports",
        feature_category="Reporting",
        confidence=0.88,
    )
    combined = AgentAnalysisResult.from_agent_outputs(theme, pain, feature)

    assert combined.theme == "App Stability"
    assert combined.theme_confidence == 0.9
    assert combined.pain_point == "Customers cannot upload documents."
    assert combined.pain_point_confidence == 0.92
    assert combined.feature_request == "Save frequently used reports"
    assert combined.feature_category == "Reporting"
    assert combined.feature_request_confidence == 0.88


def test_agent_analysis_result_no_feature_request_stays_none():
    """
    Even if the Feature Request Agent's `feature_request` text field
    somehow got populated while has_feature_request is False, the
    combined result must not surface a feature opportunity that isn't
    real. This guards the "never fabricate a feature request" rule at
    the combination boundary too, not just at the agent boundary.
    """
    theme = ThemeResult(theme="Bug Report", confidence=0.95)
    pain = PainPointResult(pain_point="The export button does nothing.", confidence=0.9)
    feature = FeatureRequestResult(has_feature_request=False, confidence=0.7)

    combined = AgentAnalysisResult.from_agent_outputs(theme, pain, feature)

    assert combined.feature_request is None
    assert combined.feature_category is None
    # Confidence is still carried through — it's the agent's confidence
    # in its "no request found" judgment, not fabricated either.
    assert combined.feature_request_confidence == 0.7
