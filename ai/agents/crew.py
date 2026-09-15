"""
ai/agents/crew.py
====================
The Milestone 2 agentic layer: exactly three agents, as scoped —

  1. Theme Extraction Agent
  2. Customer Pain Point Identification Agent
  3. Feature Request Agent

They run as one sequential CrewAI `Crew` against a single piece of
already-cleaned feedback text (Milestone 1's `analyze_feedback()`
supplies that text — this module does not clean or validate text
itself, and does not know about pandas, CSVs, or file paths at all).

TESTABILITY BY DESIGN
------------------------
`run_feedback_crew()` accepts an optional `crew_factory` parameter.
In production it's left as the default (`build_feedback_crew`, which
builds a real CrewAI `Crew` wired to a real LLM). In tests, callers
pass a fake factory that returns a lightweight stand-in object with a
`.kickoff()` method — no real crewai `Agent`/`Task`/`Crew` internals,
no network call, no API key required. This avoids depending on any
particular crewai-internal mocking point (those are provider-specific
and change across crewai versions), while still exercising every line
of the real extraction/flattening logic. See
ai/tests/test_crew.py for the fakes used this way.
"""

from __future__ import annotations

import logging
from typing import Callable, Optional

from crewai import Agent, Task, Crew, Process

from ai.agents.llm import get_llm
from ai.agents.schemas import ThemeResult, PainPointResult, FeatureRequestResult, AgentAnalysisResult

logger = logging.getLogger("ai.agents.crew")


# ---------------------------------------------------------------------
# Agents
# ---------------------------------------------------------------------
def _build_theme_agent(llm) -> Agent:
    return Agent(
        role="Customer Feedback Theme Analyst",
        goal="Identify the single main theme/topic of a piece of customer feedback.",
        backstory=(
            "You are an experienced product analyst who has read thousands of support "
            "tickets and reviews. You are excellent at distilling a piece of feedback "
            "down to a short, consistent topic label that a Product Manager could use "
            "to group similar feedback together."
        ),
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )


def _build_pain_point_agent(llm) -> Agent:
    return Agent(
        role="Customer Pain Point Investigator",
        goal="Identify the concrete problem or friction the customer actually experienced.",
        backstory=(
            "You specialize in reading between the lines of customer complaints to state "
            "the real underlying problem in one clear sentence — not a summary of the "
            "complaint's wording, but the actual friction the customer is facing."
        ),
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )


def _build_feature_agent(llm) -> Agent:
    return Agent(
        role="Feature Request Analyst",
        goal="Detect explicit or implicit feature requests in customer feedback and categorize them.",
        backstory=(
            "You are skilled at noticing both direct asks ('please add X') and implicit "
            "ones ('I wish I didn't have to do Y manually every time'). When feedback is "
            "purely a bug report or complaint with no request for new functionality, you "
            "say so honestly instead of inventing a feature request that isn't there."
        ),
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )


# ---------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------
def _build_theme_task(agent: Agent) -> Task:
    return Task(
        description=(
            "Read the following customer feedback and identify its single main theme "
            "(a short 2-5 word topic label, e.g. 'App Stability', 'Billing Accuracy', "
            "'Onboarding Experience').\n\nFeedback:\n\"\"\"{feedback_text}\"\"\""
        ),
        expected_output="A theme label and a confidence score between 0 and 1.",
        agent=agent,
        output_pydantic=ThemeResult,
    )


def _build_pain_point_task(agent: Agent) -> Task:
    return Task(
        description=(
            "Read the following customer feedback and state, in one plain sentence, the "
            "concrete problem or friction the customer experienced. Describe the problem "
            "itself, not just a restatement of their wording.\n\n"
            "Feedback:\n\"\"\"{feedback_text}\"\"\""
        ),
        expected_output="One sentence describing the pain point and a confidence score between 0 and 1.",
        agent=agent,
        output_pydantic=PainPointResult,
    )


def _build_feature_task(agent: Agent) -> Task:
    return Task(
        description=(
            "Read the following customer feedback and determine whether it contains an "
            "explicit or implicit request for new/changed functionality. If it does, "
            "describe the requested feature in the customer's intent and assign it a "
            "broad functional category (e.g. 'Reporting', 'Payments', 'Notifications', "
            "'Search', 'Performance'). If the feedback contains no feature request at "
            "all (e.g. it's purely a bug report or a compliment), set "
            "has_feature_request to false and leave feature_request/feature_category "
            "empty rather than inventing one.\n\n"
            "Feedback:\n\"\"\"{feedback_text}\"\"\""
        ),
        expected_output=(
            "has_feature_request (true/false), the feature request description and "
            "category if applicable, and a confidence score between 0 and 1."
        ),
        agent=agent,
        output_pydantic=FeatureRequestResult,
    )


# ---------------------------------------------------------------------
# Crew assembly
# ---------------------------------------------------------------------
def build_feedback_crew(feedback_text: str, llm=None) -> Crew:
    """
    Build a fresh Crew (three agents, three independent tasks) for one
    piece of feedback text. A new Crew is built per call rather than
    reused/cached — CrewAI agents/tasks are lightweight, cheap to
    construct, and this keeps each analysis fully isolated (no shared
    mutable state between concurrent requests from the backend).
    """
    llm = llm or get_llm()

    theme_agent = _build_theme_agent(llm)
    pain_point_agent = _build_pain_point_agent(llm)
    feature_agent = _build_feature_agent(llm)

    tasks = [
        _build_theme_task(theme_agent),
        _build_pain_point_task(pain_point_agent),
        _build_feature_task(feature_agent),
    ]

    return Crew(
        agents=[theme_agent, pain_point_agent, feature_agent],
        tasks=tasks,
        process=Process.sequential,
        verbose=False,
    )


def run_feedback_crew(
    feedback_text: str,
    *,
    crew_factory: Optional[Callable[[str], "Crew"]] = None,
) -> AgentAnalysisResult:
    """
    Run the three-agent crew on one piece of feedback text and return
    a combined, structured `AgentAnalysisResult`.

    Parameters
    ----------
    feedback_text:
        Already-cleaned feedback text (see ai.preprocessing.cleaning).
    crew_factory:
        Advanced/testing hook. A callable that takes `feedback_text`
        and returns an object with a `.kickoff(inputs=...)` method
        (either a real `crewai.Crew` or a test fake). Defaults to
        `build_feedback_crew`. Production code should never need to
        pass this — it exists so tests can inject a fake crew without
        any network access or API key.

    Raises
    ------
    ai.agents.llm.LLMNotConfiguredError
        If no GenAI provider is configured (propagated from
        `get_llm()`, invoked inside the default `crew_factory`).
    Exception
        Any error from the underlying LLM call/crew execution is
        propagated as-is — the caller (feedback_analyzer.py) is
        responsible for catching it and reporting `ai_status: "failed"`
        rather than silently returning fabricated results.
    """
    factory = crew_factory or build_feedback_crew
    crew = factory(feedback_text)

    logger.info("Running feedback crew")
    crew_output = crew.kickoff(inputs={"feedback_text": feedback_text})

    tasks_output = crew_output.tasks_output
    theme_result: ThemeResult = tasks_output[0].pydantic
    pain_point_result: PainPointResult = tasks_output[1].pydantic
    feature_result: FeatureRequestResult = tasks_output[2].pydantic

    if theme_result is None or pain_point_result is None or feature_result is None:
        # The LLM responded, but crewai couldn't parse it into our
        # pydantic schema (e.g. the model ignored the expected format).
        # Treat this the same as any other analysis failure rather
        # than returning a partially-None "success".
        raise ValueError(
            "One or more agents did not return a structured result that matched "
            "the expected schema (theme/pain_point/feature_request)."
        )

    return AgentAnalysisResult.from_agent_outputs(theme_result, pain_point_result, feature_result)
