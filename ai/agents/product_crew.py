"""
ai/agents/product_crew.py
============================
Milestone 3 content-generation agents: PRD, User Stories, Acceptance
Criteria, and the explanation half of prioritization.

WHY THESE ARE SEPARATE SINGLE-AGENT "CREWS", NOT ONE BIG MULTI-AGENT CREW
-----------------------------------------------------------------------------
Milestone 2's `ai/agents/crew.py` runs three agents TOGETHER because
all three genuinely analyze the SAME piece of feedback in one pass -
that's a real multi-agent workflow. PRD generation, user story
generation, acceptance criteria generation, and priority explanation
are different: each is a standalone generation task, typically
triggered separately by a PM clicking a different button at a
different time (generate a PRD today, add user stories tomorrow,
regenerate the priority explanation after new feedback comes in).
Treating each as its own single-agent, single-task "crew" (reusing the
exact same `Agent` + `Task(output_pydantic=...)` + `Crew` + `kickoff()`
pattern Milestone 2 established) keeps them independently callable,
independently testable, and avoids forcing an artificial collaboration
between agents that don't actually need to talk to each other. This is
a deliberate choice to avoid the "unnecessary additional agents /
complicated orchestration" trap, not an oversight.

ALL FOUR SHARE:
- The same `get_llm()` provider configuration as Milestone 2 (no new
  config, no new environment variables).
- The same `crew_factory` dependency-injection testing pattern as
  `ai.agents.crew.run_feedback_crew` (see ai/tests/test_product_crew.py)
  - no network access or API key required to test the extraction
    logic.
- The same anti-hallucination approach: the prompt explicitly
  instructs the agent to use ONLY the supplied context, and to leave a
  field empty/null rather than invent content for it. See
  ai/agents/context.py for how that context is formatted.
"""

from __future__ import annotations

import logging
from typing import Callable, Optional

from crewai import Agent, Task, Crew, Process

from ai.agents.llm import get_llm
from ai.agents.context import format_context_block
from ai.agents.schemas import (
    PRDResult,
    UserStoriesResult,
    AcceptanceCriteriaResult,
    PriorityExplanationResult,
)

logger = logging.getLogger("ai.agents.product_crew")


# ---------------------------------------------------------------------
# Shared anti-hallucination instruction, reused verbatim in every
# task description below so the rule is stated identically everywhere
# rather than reworded (and possibly weakened) per-prompt.
# ---------------------------------------------------------------------
_GROUNDING_RULE = (
    "IMPORTANT: Base your answer ONLY on the context provided below. "
    "Do not invent customer feedback, statistics, or facts that are not "
    "present in the context. If the context does not contain enough "
    "information for a section, leave that field empty (or an empty list) "
    "rather than guessing. If you need to make a reasonable inference that "
    "is NOT directly stated in the context, put it in the assumptions field "
    "instead of presenting it as a fact elsewhere."
)


# =======================================================================
# PRD GENERATION
# =======================================================================
def _build_prd_agent(llm) -> Agent:
    return Agent(
        role="Product Requirements Analyst",
        goal="Turn customer feedback evidence into a clear, structured PRD a Product Manager can act on.",
        backstory=(
            "You are a product analyst who writes precise, evidence-based PRDs. You never "
            "pad a PRD with generic filler - every section is either backed by the evidence "
            "you were given, explicitly marked as an assumption, or left empty."
        ),
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )


def _build_prd_task(agent: Agent, context_text: str) -> Task:
    return Task(
        description=(
            f"Write a structured PRD (Product Requirements Document) for the feature "
            f"described in the context below.\n\n{_GROUNDING_RULE}\n\n"
            f"Context:\n{context_text}"
        ),
        expected_output="A complete PRDResult with every section either filled from the context, marked as an assumption, or left empty.",
        agent=agent,
        output_pydantic=PRDResult,
    )


def build_prd_crew(context: dict, llm=None) -> Crew:
    llm = llm or get_llm()
    agent = _build_prd_agent(llm)
    task = _build_prd_task(agent, format_context_block(context))
    return Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=False)


def run_prd_crew(context: dict, *, crew_factory: Optional[Callable[[dict], "Crew"]] = None) -> PRDResult:
    """Run PRD generation and return the structured result. See run_feedback_crew() in ai/agents/crew.py for the identical error-propagation contract."""
    factory = crew_factory or build_prd_crew
    crew = factory(context)
    logger.info("Running PRD generation crew")
    crew_output = crew.kickoff(inputs={})
    result: PRDResult = crew_output.tasks_output[0].pydantic
    if result is None:
        raise ValueError("PRD agent did not return a structured result matching PRDResult.")
    return result


# =======================================================================
# USER STORY GENERATION
# =======================================================================
def _build_user_story_agent(llm) -> Agent:
    return Agent(
        role="User Story Writer",
        goal="Write clear, standard-format user stories derived from real customer context.",
        backstory=(
            "You write user stories in the 'As a / I want / so that' format for engineering "
            "teams. Every story you write is traceable to an actual pain point or feature "
            "request you were given - you don't invent user needs that weren't evidenced."
        ),
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )


def _build_user_story_task(agent: Agent, context_text: str) -> Task:
    return Task(
        description=(
            f"Write 1 to 5 user stories (however many are genuinely supported by the context "
            f"- do not pad to reach a target count) for the feature described below, in the "
            f"standard 'As a [user], I want [capability], so that [benefit]' format.\n\n"
            f"{_GROUNDING_RULE}\n\nContext:\n{context_text}"
        ),
        expected_output="A UserStoriesResult containing 1-5 user stories, each grounded in the supplied pain points/feature requests.",
        agent=agent,
        output_pydantic=UserStoriesResult,
    )


def build_user_story_crew(context: dict, llm=None) -> Crew:
    llm = llm or get_llm()
    agent = _build_user_story_agent(llm)
    task = _build_user_story_task(agent, format_context_block(context))
    return Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=False)


def run_user_story_crew(context: dict, *, crew_factory: Optional[Callable[[dict], "Crew"]] = None) -> UserStoriesResult:
    factory = crew_factory or build_user_story_crew
    crew = factory(context)
    logger.info("Running user story generation crew")
    crew_output = crew.kickoff(inputs={})
    result: UserStoriesResult = crew_output.tasks_output[0].pydantic
    if result is None:
        raise ValueError("User story agent did not return a structured result matching UserStoriesResult.")
    return result


# =======================================================================
# ACCEPTANCE CRITERIA GENERATION
# =======================================================================
def _build_acceptance_criteria_agent(llm) -> Agent:
    return Agent(
        role="QA / Acceptance Criteria Writer",
        goal="Write specific, testable acceptance criteria for a given user story.",
        backstory=(
            "You write acceptance criteria the way a QA engineer would - specific and "
            "testable, never vague statements like 'the feature should work properly'. "
            "Each criterion describes one clear, checkable condition."
        ),
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )


def _build_acceptance_criteria_task(agent: Agent, user_story_text: str, context_text: str) -> Task:
    return Task(
        description=(
            f"Write acceptance criteria for this user story:\n\"{user_story_text}\"\n\n"
            f"Each criterion must be specific and testable (e.g. describe a concrete input, "
            f"action, or condition and the expected result) - never a vague statement like "
            f"'the feature should work properly'. Assign each one a MoSCoW priority: "
            f"'Must', 'Should', or 'Could'. Give each criterion a sequential local id "
            f'starting at "AC-1".\n\n{_GROUNDING_RULE}\n\n'
            f"Supporting context (for grounding, not every criterion needs to cite it):\n{context_text}"
        ),
        expected_output="An AcceptanceCriteriaResult with specific, testable criteria, each with an id and a MoSCoW priority.",
        agent=agent,
        output_pydantic=AcceptanceCriteriaResult,
    )


def build_acceptance_criteria_crew(user_story_text: str, context: dict, llm=None) -> Crew:
    llm = llm or get_llm()
    agent = _build_acceptance_criteria_agent(llm)
    task = _build_acceptance_criteria_task(agent, user_story_text, format_context_block(context))
    return Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=False)


def run_acceptance_criteria_crew(
    user_story_text: str,
    context: dict,
    *,
    crew_factory: Optional[Callable[[str, dict], "Crew"]] = None,
) -> AcceptanceCriteriaResult:
    factory = crew_factory or build_acceptance_criteria_crew
    crew = factory(user_story_text, context)
    logger.info("Running acceptance criteria generation crew")
    crew_output = crew.kickoff(inputs={})
    result: AcceptanceCriteriaResult = crew_output.tasks_output[0].pydantic
    if result is None:
        raise ValueError("Acceptance criteria agent did not return a structured result matching AcceptanceCriteriaResult.")
    return result


# =======================================================================
# PRIORITIZATION EXPLANATION
# =======================================================================
# NOTE: this agent NEVER computes the priority score itself - it only
# explains a score that was already computed deterministically by
# ai/services/prioritization.py's calculate_rice_score(). The score is
# passed IN as part of the context (see ai/agents/context.py
# PriorityInfo) purely for the agent to reference while explaining,
# never for it to decide or adjust.
def _build_priority_explanation_agent(llm) -> Agent:
    return Agent(
        role="Prioritization Analyst",
        goal="Explain, in plain language, why a feature's RICE score makes sense given the evidence - never invent or adjust the score itself.",
        backstory=(
            "You explain prioritization decisions to Product Managers and stakeholders. You "
            "are given an already-calculated score and your job is only to explain it using "
            "real evidence - you never state or imply a different numeric score than the one "
            "you were given."
        ),
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )


def _build_priority_explanation_task(agent: Agent, context_text: str) -> Task:
    return Task(
        description=(
            f"A RICE priority score has already been calculated for this feature (see "
            f"'Priority information' in the context below) - do NOT recompute, restate as "
            f"different, or second-guess that score. Your job is only to explain, in plain "
            f"language, why that score makes sense (or what evidence pulls it higher or "
            f"lower), grounded in the pain points and evidence provided.\n\n"
            f"{_GROUNDING_RULE}\n\nContext:\n{context_text}"
        ),
        expected_output="A PriorityExplanationResult explaining the already-given score, grounded in the supplied pain points/evidence.",
        agent=agent,
        output_pydantic=PriorityExplanationResult,
    )


def build_priority_explanation_crew(context: dict, llm=None) -> Crew:
    llm = llm or get_llm()
    agent = _build_priority_explanation_agent(llm)
    task = _build_priority_explanation_task(agent, format_context_block(context))
    return Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=False)


def run_priority_explanation_crew(
    context: dict,
    *,
    crew_factory: Optional[Callable[[dict], "Crew"]] = None,
) -> PriorityExplanationResult:
    factory = crew_factory or build_priority_explanation_crew
    crew = factory(context)
    logger.info("Running priority explanation crew")
    crew_output = crew.kickoff(inputs={})
    result: PriorityExplanationResult = crew_output.tasks_output[0].pydantic
    if result is None:
        raise ValueError("Priority explanation agent did not return a structured result matching PriorityExplanationResult.")
    return result
