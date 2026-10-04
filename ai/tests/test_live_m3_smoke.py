"""
ai/tests/test_live_m3_smoke.py
=================================
OPTIONAL LIVE LLM SMOKE TESTS - these make real calls to whichever
GenAI provider is configured in your .env (real API usage, real
latency, real cost if using a paid provider). Everything else in
ai/tests/ runs with zero network access and zero API key; these are
the deliberate exception, kept in their own file so they're easy to
include or exclude.

SKIPPED BY DEFAULT. To run them:

    Windows (PowerShell):  $env:RUN_LIVE_LLM_TESTS="1"; pytest ai\\tests\\test_live_m3_smoke.py -v
    Windows (cmd):         set RUN_LIVE_LLM_TESTS=1 && pytest ai\\tests\\test_live_m3_smoke.py -v
    macOS/Linux:            RUN_LIVE_LLM_TESTS=1 pytest ai/tests/test_live_m3_smoke.py -v

Requires a configured GEMINI_API_KEY or OPENAI_API_KEY in .env (see
ai/README.md "Milestone 2 setup" - the same provider config M3 reuses
unchanged). These are intentionally loose "does it run and come back
with something plausible" checks, not exact-output assertions - an
LLM's exact wording will vary between runs, that's expected and fine.
"""

import os
import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from ai.services.prd_generator import generate_prd  # noqa: E402
from ai.services.user_story_generator import generate_user_stories, generate_acceptance_criteria  # noqa: E402
from ai.services.product_assistant import ask_assistant  # noqa: E402
from ai.services.prioritization import explain_priority  # noqa: E402

_LIVE = pytest.mark.skipif(
    os.getenv("RUN_LIVE_LLM_TESTS") != "1",
    reason="Live LLM test - set RUN_LIVE_LLM_TESTS=1 to run (uses real API quota).",
)

_SAMPLE_CONTEXT = {
    "feature_name": "Save frequently used reports",
    "themes": ["Reporting"],
    "pain_points": ["Regenerating the same report every time is tedious."],
    "feature_requests": ["Save frequently used reports"],
    "supporting_evidence": [
        {"feedback_id": "42", "text": "I wish I could save my frequently used reports so I don't have to generate them every time."}
    ],
}


@_LIVE
def test_live_generate_prd():
    result = generate_prd(_SAMPLE_CONTEXT, feature_id="feat-live-1")
    print("\nLIVE PRD RESULT:", result)
    assert result["status"] == "ai_draft", f"Expected success, got: {result}"
    assert result["prd"]["title"]
    assert isinstance(result["prd"]["customer_pain_points"], list)


@_LIVE
def test_live_generate_user_stories_and_acceptance_criteria():
    stories_result = generate_user_stories(_SAMPLE_CONTEXT, feature_id="feat-live-1")
    print("\nLIVE USER STORIES RESULT:", stories_result)
    assert stories_result["status"] == "ai_draft", f"Expected success, got: {stories_result}"
    assert len(stories_result["user_stories"]) >= 1

    first_story = stories_result["user_stories"][0]["user_story"]
    ac_result = generate_acceptance_criteria(first_story, _SAMPLE_CONTEXT)
    print("\nLIVE ACCEPTANCE CRITERIA RESULT:", ac_result)
    assert ac_result["status"] == "ai_draft", f"Expected success, got: {ac_result}"
    assert len(ac_result["acceptance_criteria"]) >= 1


@_LIVE
def test_live_assistant_grounded_question():
    result = ask_assistant("What customer feedback supports this feature?", _SAMPLE_CONTEXT)
    print("\nLIVE ASSISTANT RESULT (grounded question):", result)
    assert result["status"] == "completed", f"Expected success, got: {result}"
    assert result["grounded"] is True, "Expected a grounded answer given rich supporting context"


@_LIVE
def test_live_assistant_honestly_says_unavailable_for_ungrounded_question():
    result = ask_assistant("What is our company's total annual revenue?", _SAMPLE_CONTEXT)
    print("\nLIVE ASSISTANT RESULT (ungrounded question):", result)
    assert result["status"] == "completed", f"Expected success, got: {result}"
    assert result["grounded"] is False, (
        "Expected the assistant to say this information is unavailable rather than guessing - "
        f"got: {result['answer']}"
    )


@_LIVE
def test_live_priority_explanation():
    result = explain_priority(_SAMPLE_CONTEXT, reach=1000, impact=2, confidence=0.8, effort=3, feature_id="feat-live-1")
    print("\nLIVE PRIORITY EXPLANATION RESULT:", result)
    assert result["priority_score"] == 533.33  # deterministic regardless of LLM
    assert result["ai_status"] == "completed", f"Expected success, got: {result}"
    assert result["impact_reasoning"]
