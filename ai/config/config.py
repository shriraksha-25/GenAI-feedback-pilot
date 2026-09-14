"""
ai/config/config.py
=====================
Single source of truth for paths, column mapping, and environment
variables used by the AI module.

WHY THIS FILE EXISTS
----------------------
So no other file ever hardcodes a file path, column name, or reads
os.environ directly. If a path or setting needs to change, it changes
here once.

ENVIRONMENT VARIABLES
-----------------------
This project optionally reads a `.env` file (see root `.env.example`)
using python-dotenv, if it's installed. This lets each teammate keep
their own secrets (API keys, DB URI) locally, out of Git, while the
AI module still knows what variable NAMES to expect.

None of these variables are required for Milestone 1 — they're wired
up now so Milestone 2 (which will call an LLM) doesn't need a config
rewrite later.
"""

from __future__ import annotations

import os
from pathlib import Path

try:
    # python-dotenv is optional. If a teammate hasn't installed it yet,
    # the AI module still runs fine using whatever is already in the
    # real environment (or falls back to defaults below).
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

# ---------------------------------------------------------------------
# 1. PROJECT PATHS (all relative — safe to clone anywhere, any OS)
# ---------------------------------------------------------------------
# This file lives at <repo>/ai/config/config.py.
# .parent x3 -> config -> ai -> <repo root>. We anchor everything to
# the "ai" package folder specifically (not the monorepo root) so the
# AI module keeps working even if someone runs/tests it standalone,
# outside the full monorepo checkout.
AI_MODULE_ROOT = Path(__file__).resolve().parent.parent

RAW_DATA_DIR = AI_MODULE_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = AI_MODULE_ROOT / "data" / "processed"
SAMPLE_DATA_DIR = AI_MODULE_ROOT / "data" / "sample"

RAW_CSV_PATH = RAW_DATA_DIR / "customer_support_tickets.csv"
SAMPLE_CSV_PATH = SAMPLE_DATA_DIR / "sample_feedback.csv"
CLEANED_CSV_PATH = PROCESSED_DATA_DIR / "cleaned_feedback.csv"
QUALITY_REPORT_PATH = PROCESSED_DATA_DIR / "data_quality_report.json"

# ---------------------------------------------------------------------
# 2. ENVIRONMENT VARIABLES (all optional for Milestone 1)
# ---------------------------------------------------------------------
# AI_MODEL: which AI backend Milestone 2+ should use, e.g. "openai",
# "gemini", "local-embedding". Not read by any Milestone 1 code path.
AI_MODEL = os.getenv("AI_MODEL", "not_configured")

# API keys for whichever LLM provider Milestone 2 ends up using.
# Never given a real default — an unset key should stay unset, not
# silently become an empty string that looks like "it's configured".
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Used only if/when the AI module talks to MongoDB directly (not
# needed for Milestone 1 — see docs/AI_INTEGRATION.md "Database
# separation"). The database teammate owns the real value.
MONGODB_URI = os.getenv("MONGODB_URI")

# ---------------------------------------------------------------------
# 3. KAGGLE RAW COLUMN NAME -> OUR NORMALIZED SCHEMA
# ---------------------------------------------------------------------
# See ai/schemas/feedback.py for what these normalized names mean.
# ASSUMPTION: reflects the Kaggle "Customer Support Ticket Dataset by
# Suraj" column headers at the time this project was written — verify
# against your actual downloaded file with analysis/dataset_analysis.py
# and edit this map if your file's headers differ.
COLUMN_MAP = {
    "Ticket ID": "feedback_id",
    "Customer Name": "customer_name",
    "Customer Email": "customer_email",
    "Customer Age": "customer_age",
    "Customer Gender": "customer_gender",
    "Product Purchased": "product",
    "Date of Purchase": "created_at",
    "Ticket Type": "ticket_type",
    "Ticket Subject": "subject",
    "Ticket Description": "description",
    "Ticket Status": "status",
    "Resolution": "resolution",
    "Ticket Priority": "priority",
    "Ticket Channel": "channel",
    "First Response Time": "first_response_time",
    "Time to Resolution": "time_to_resolution",
    "Customer Satisfaction Rating": "customer_satisfaction",
}

# The normalized fields that make it into our canonical schema
# (see ai/schemas/feedback.py CANONICAL_FIELDS). Identity fields
# (customer_name/email) are deliberately excluded.
USEFUL_COLUMNS = [
    "feedback_id",
    "product",
    "ticket_type",
    "subject",
    "description",
    "priority",
    "channel",
    "status",
    "customer_satisfaction",
    "created_at",
]

CORE_TEXT_FIELDS = ["subject", "description"]

# ---------------------------------------------------------------------
# 4. MISC SETTINGS
# ---------------------------------------------------------------------
MIN_DESCRIPTION_LENGTH = 15
RANDOM_SEED = 42
