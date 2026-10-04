"""
ai/agents/assistant_crew.py
==============================
The Product Intelligence Assistant - a single grounded question-
answering agent, NOT a generic chatbot and NOT a multi-agent crew.

WHAT THIS ASSISTANT DOES
----------------------------
Answers a Product Manager's question using ONLY the project context
it's given (themes, pain points, feature requests, supporting
feedback, a previously-generated PRD, priority explanation, etc. - see
ai/agents/context.py for the exact shape). If the answer isn't in the
supplied context, it says so (`grounded: False`) instead of guessing -
this is enforced the same way as every other M3 agent: by instruction
in the prompt plus a structured output field the backend can check.

WHAT THIS ASSISTANT DELIBERATELY DOES NOT DO
--------------------------------------------------
It does NOT try to detect "action" requests like "generate a PRD for
this feature" or "generate user stories" and route them internally to
`generate_prd()` / `generate_user_stories()`. Those are separate,
already-structured functions (ai/services/prd_generator.py,
ai/services/user_story_generator.py) with their own schemas - the
frontend should call them directly (e.g. from a "Generate PRD" button)
rather than asking this assistant to parse free-text intent into an
action. Building reliable intent-detection on top of a grounded-QA
agent is a meaningfully different, more complex problem (and an easy
place to introduce bugs that are hard to demo confidently), so it's
left as a clearly-documented boundary rather than attempted partially.
See docs/AI_INTEGRATION.md "Product Intelligence Assistant" for the
full explanation, including why this doesn't need RAG/a vector
database at this project's scale.

NO RAG / NO VECTOR DATABASE
--------------------------------
This assistant does not retrieve anything itself. The backend is
responsible for deciding what context is relevant to a question (e.g.
"which feature is the PM currently looking at in the UI") and passing
it in directly, the same way ai/agents/product_crew.py's functions
work. For a project at this scale (a bounded set of features/feedback
per workspace, not an open-ended corpus), the database team's existing
MongoDB querying is sufficient "retrieval" - adding a vector database
and embedding-based retrieval on top would be meaningfully more
infrastructure for no clear benefit yet. If a later milestone needs to
search across a much larger, unbounded feedback corpus, that's the
point to reconsider.
"""

from __future__ import annotations

import logging
from typing import Callable, Optional

from crewai import Agent, Task, Crew, Process

from ai.agents.llm import get_llm
from ai.agents.context import format_context_block
from ai.agents.schemas import AssistantResponse

logger = logging.getLogger("ai.agents.assistant_crew")


def _build_assistant_agent(llm) -> Agent:
    return Agent(
        role="Product Intelligence Assistant",
        goal="Answer a Product Manager's question about a feature using only the supplied project context, never general knowledge or invented facts.",
        backstory=(
            "You are a product intelligence assistant embedded in a product management tool. "
            "You are not a general-purpose chatbot - you only know what is in the context you "
            "are given for this specific workspace/feature. When the context doesn't contain "
            "the answer, you say so plainly instead of guessing or using outside knowledge."
        ),
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )


def _build_assistant_task(agent: Agent, question: str, context_text: str) -> Task:
    return Task(
        description=(
            f"Answer this Product Manager's question:\n\"{question}\"\n\n"
            f"Use ONLY the context below. Do not use general knowledge about products, "
            f"companies, or best practices that isn't grounded in this specific context. "
            f"If the context does not contain enough information to answer, set grounded to "
            f"false and say plainly in the answer that this information is not available in "
            f"the current project context, rather than guessing. When you do use specific "
            f"pieces of supporting evidence, list their feedback_ids in "
            f"referenced_feedback_ids.\n\nContext:\n{context_text}"
        ),
        expected_output="An AssistantResponse: an answer grounded in the context, with grounded=false and an honest 'not available' answer if the context doesn't support one.",
        agent=agent,
        output_pydantic=AssistantResponse,
    )


def build_assistant_crew(question: str, context: dict, llm=None) -> Crew:
    llm = llm or get_llm()
    agent = _build_assistant_agent(llm)
    task = _build_assistant_task(agent, question, format_context_block(context))
    return Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=False)


def run_assistant_crew(
    question: str,
    context: dict,
    *,
    crew_factory: Optional[Callable[[str, dict], "Crew"]] = None,
) -> AssistantResponse:
    """Run the assistant on one question and return the structured answer. Same error-propagation contract as ai.agents.crew.run_feedback_crew()."""
    factory = crew_factory or build_assistant_crew
    crew = factory(question, context)
    logger.info("Running Product Intelligence Assistant")
    crew_output = crew.kickoff(inputs={})
    result: AssistantResponse = crew_output.tasks_output[0].pydantic
    if result is None:
        raise ValueError("Assistant agent did not return a structured result matching AssistantResponse.")
    return result
