"""
ai/agents/llm.py
==================
Builds the CrewAI-compatible LLM object the three agents share, based
purely on environment configuration (ai/config/config.py) — never a
hardcoded key, never a hardcoded provider choice baked into code.

WHICH PROVIDER?
-----------------
Milestone 1 left both OPENAI_API_KEY and GEMINI_API_KEY as blank
placeholders in .env.example with AI_MODEL="not_configured" — no
provider had actually been chosen or wired up yet. For Milestone 2:

  RECOMMENDATION: Google Gemini (gemini/gemini-2.5-flash), because
  - it has a genuinely free tier suitable for a student project
    (OpenAI's API is pay-as-you-go with no meaningful free quota),
  - CrewAI supports it as a first-class native provider, and
  - it's fast enough for three short structured-extraction calls per
    piece of feedback.

  Google retires older Gemini versions on a rolling basis (1.0, 1.5,
  and 2.0 Flash have all been shut down as of this writing) — if the
  configured model starts returning 404 NOT_FOUND, list the models
  your own key currently supports and update AI_MODEL in .env:

    python -c "from google import genai; import os; from dotenv import load_dotenv; load_dotenv(); client = genai.Client(api_key=os.environ['GEMINI_API_KEY']); [print(m.name) for m in client.models.list() if 'generateContent' in (m.supported_actions or [])]"

That said, this module does NOT hardcode that choice — it picks
whichever provider is actually configured, preferring OpenAI if both
are set (since OpenAI needs no extra package beyond base `crewai`).
See .env.example and ai/README.md for exact setup steps.

NO FAKE OUTPUT ON MISCONFIGURATION
-------------------------------------
If neither key is set, `get_llm()` raises `LLMNotConfiguredError`
rather than returning some default/dummy LLM. The caller
(ai/agents/crew.py -> ai/services/feedback_analyzer.py) is expected to
catch this and report `ai_status: "not_configured"` — never a
fabricated theme/pain-point/feature result.
"""

from __future__ import annotations

from ai.config.config import AI_MODEL, OPENAI_API_KEY, GEMINI_API_KEY

# Default model names used only when AI_MODEL itself is left at its
# "not_configured" placeholder but an API key IS present — i.e. the
# person configured a key but didn't pick a specific model string.
#
# IMPORTANT: Google and OpenAI retire/rename model versions
# periodically (e.g. all Gemini 1.0 and 1.5 models, and Gemini 2.0
# Flash, have since been shut down and now return 404 NOT_FOUND).
# Treat these defaults as a starting point, not a guarantee — if you
# get a 404 "model not found" error, list the models YOUR key can
# actually use and update AI_MODEL in .env accordingly:
#
#   python -c "from google import genai; import os; from dotenv import load_dotenv; load_dotenv(); client = genai.Client(api_key=os.environ['GEMINI_API_KEY']); [print(m.name) for m in client.models.list() if 'generateContent' in (m.supported_actions or [])]"
#
_DEFAULT_OPENAI_MODEL = "gpt-4o-mini"
_DEFAULT_GEMINI_MODEL = "gemini/gemini-2.5-flash"


class LLMNotConfiguredError(RuntimeError):
    """
    Raised when no GenAI provider is configured. This is an expected,
    handled condition (see feedback_analyzer.py) — not a bug — so it
    gets its own exception type instead of a bare RuntimeError.
    """


def get_llm():
    """
    Return a configured `crewai.LLM` instance, or raise
    `LLMNotConfiguredError` if no provider is set up.

    Provider selection:
    - OPENAI_API_KEY set  -> OpenAI (model = AI_MODEL if it looks like
      an OpenAI model name, else the default gpt-4o-mini).
    - else GEMINI_API_KEY set -> Gemini (model = AI_MODEL if it starts
      with "gemini/", else the default gemini/gemini-2.5-flash).
      Requires the optional `google-genai` extra — see ai/requirements.txt.
    - neither set -> LLMNotConfiguredError with setup instructions.
    """
    from crewai import LLM  # imported lazily so importing this module never requires crewai to be installed unless actually used

    if OPENAI_API_KEY:
        model = AI_MODEL if AI_MODEL and not AI_MODEL.startswith("gemini/") and AI_MODEL != "not_configured" else _DEFAULT_OPENAI_MODEL
        return LLM(model=model, api_key=OPENAI_API_KEY)

    if GEMINI_API_KEY:
        model = AI_MODEL if AI_MODEL and AI_MODEL.startswith("gemini/") else _DEFAULT_GEMINI_MODEL
        return LLM(model=model, api_key=GEMINI_API_KEY)

    raise LLMNotConfiguredError(
        "No GenAI provider is configured. Set OPENAI_API_KEY or GEMINI_API_KEY "
        "in your .env (copy .env.example -> .env first). "
        "Recommended for this project: GEMINI_API_KEY with AI_MODEL=gemini/gemini-2.5-flash "
        "(get a free key at https://aistudio.google.com/apikey). "
        "See ai/README.md 'Milestone 2 setup' for exact steps."
    )
