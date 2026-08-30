"""
ai/schemas/feedback.py
========================
The SINGLE SOURCE OF TRUTH for what a "feedback record" looks like,
shared conceptually across the AI module, the FastAPI backend, and
MongoDB. If any of the three needs a new field, it should be added
here first and then propagated — not invented independently in three
places.

WHY DATACLASSES INSTEAD OF PYDANTIC
--------------------------------------
The backend team may well use Pydantic (FastAPI's usual choice) for
their own request/response models — that's their call. This module
avoids taking a hard dependency on Pydantic so the AI module stays
installable with just `pip install -r ai/requirements.txt` and no
FastAPI-specific packages. `to_dict()` on each dataclass below returns
a plain, JSON-compatible dict, which converts to a Pydantic model (or
straight to JSON, or straight to a MongoDB document) with zero
friction on the backend side.

THREE DISTINCT LAYERS — DO NOT MIX THEM UP
---------------------------------------------
1. RAW dataset fields  — whatever the Kaggle CSV happens to call them.
   Only `config.COLUMN_MAP` and `analysis/dataset_analysis.py` should
   ever reference these raw names.
2. NORMALIZED fields    — our own stable names (`feedback_id`,
   `description`, ...). Everything in this module, `preprocessing/`,
   `pipeline/`, and `services/` uses ONLY these names.
3. AI-GENERATED fields  — `sentiment`, `category`, `theme`,
   `pain_point`, `feature_opportunity`. Always `None` in Milestone 1.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Optional


# ---------------------------------------------------------------------
# LAYER 2: normalized feedback record (what the AI module works with)
# ---------------------------------------------------------------------
@dataclass
class FeedbackRecord:
    """
    One normalized piece of customer feedback (e.g. one support
    ticket), independent of which raw dataset it came from.

    Field ownership (who is expected to set/maintain each field):
    - feedback_id, source, product, ticket_type, subject, description,
      priority, status, channel, customer_satisfaction, created_at:
      populated by whoever creates the record — either this AI module
      (when loading the Kaggle CSV) or the backend (when a real user
      submits feedback through the API).
    - ai_analysis: owned by the AI module. Backend/database should
      treat it as read-only output, not something they compute.
    """

    feedback_id: str
    source: str  # e.g. "support_ticket", "review", "manual_entry"
    product: Optional[str] = None
    ticket_type: Optional[str] = None
    subject: Optional[str] = None
    description: str = ""
    priority: Optional[str] = None
    status: Optional[str] = None
    channel: Optional[str] = None
    customer_satisfaction: Optional[float] = None
    created_at: Optional[str] = None
    ai_analysis: "AIAnalysis" = field(default_factory=lambda: AIAnalysis())

    def to_dict(self) -> dict:
        """JSON/Mongo-compatible plain dict."""
        return asdict(self)


# ---------------------------------------------------------------------
# LAYER 3: AI-generated fields — the "future" part of the schema
# ---------------------------------------------------------------------
@dataclass
class AIAnalysis:
    """
    All fields here are None until Milestone 2+ actually implements
    the corresponding analysis. Milestone 1 code must never invent a
    value for these — see README "Code quality" / "No fabricated
    results" rule.
    """

    sentiment: Optional[str] = None
    category: Optional[str] = None
    theme: Optional[str] = None
    pain_point: Optional[str] = None
    feature_opportunity: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


# ---------------------------------------------------------------------
# API-LEVEL CONTRACTS (what the backend sends/receives)
# ---------------------------------------------------------------------
def build_mongo_document(record: FeedbackRecord) -> dict:
    """
    Convert a FeedbackRecord into exactly the document shape the
    database teammate should store in MongoDB. This is the ONE place
    that defines that shape — see docs/AI_INTEGRATION.md section
    "AI <-> MongoDB contract" for the same structure with explanation.
    """
    return record.to_dict()


def empty_ai_analysis_dict() -> dict:
    """Convenience helper: the all-None ai_analysis sub-document."""
    return AIAnalysis().to_dict()
