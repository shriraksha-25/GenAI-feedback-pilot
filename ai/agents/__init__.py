# Makes "agents" a Python package.
#
# This subpackage holds the Milestone 2 CrewAI agentic layer: the
# three agents (Theme, Pain Point, Feature Request), their tasks, the
# crew that runs them, and the small LLM-provider factory they share.
#
# Nothing in this package is imported directly by the backend — the
# public entry point remains ai/services/feedback_analyzer.py, which
# calls into ai.agents.crew internally. See docs/AI_INTEGRATION.md.
