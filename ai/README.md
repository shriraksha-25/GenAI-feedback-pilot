# AI Module — AI Product Manager Copilot

This is the AI/Python module: Milestone 1, now restructured to be a
**modular, testable, importable component** of the team's monorepo
rather than a standalone script collection. If you're the backend
teammate, you want `../docs/AI_INTEGRATION.md`, not this file.

## Folder structure

```
ai/
├── __init__.py
├── config/
│   └── config.py            # paths, env vars, column mapping — single source of truth
├── schemas/
│   └── feedback.py          # canonical FeedbackRecord / AIAnalysis shape
├── preprocessing/
│   └── cleaning.py          # small, testable cleaning functions
├── pipeline/
│   └── feedback_pipeline.py # batch: clean a whole CSV, offline/dev tool
├── services/
│   └── feedback_analyzer.py # ★ PUBLIC INTERFACE — what the backend imports
├── analysis/
│   └── dataset_analysis.py  # look-only dataset inspection
├── data/
│   ├── raw/       # put the real Kaggle CSV here (gitignored)
│   ├── processed/ # pipeline output lands here (gitignored)
│   └── sample/    # small SYNTHETIC sample_feedback.csv (committed)
├── tests/
│   ├── test_preprocessing.py
│   ├── test_feedback_analyzer.py
│   └── test_pipeline.py
└── requirements.txt
```

**Why this shape?** `services/` is the only folder a teammate outside
this module should ever import from — it's the "front door." Everything
else (`preprocessing`, `pipeline`, `analysis`, `config`) is an
implementation detail `services/feedback_analyzer.py` builds on, but
none of it is exposed directly. This is a standard layered design:
interface layer (`services/`) on top of logic layers (`preprocessing/`,
`pipeline/`) on top of configuration (`config/`, `schemas/`).

## Two very different ways this module gets used

1. **Real-time, one record at a time** (what the backend calls):
   `services/feedback_analyzer.analyze_feedback(text, ...)`. No file
   I/O, no pandas exposed to the caller, returns a plain dict in
   milliseconds. This is the only thing FastAPI needs.
2. **Batch, offline, one CSV at a time** (what *you* run manually to
   prepare a dataset for analysis/demoing): `pipeline/feedback_pipeline.py`.
   Reads a CSV, cleans thousands of rows, writes a cleaned CSV + a
   JSON quality report. The backend never calls this directly.

Both use the *same* cleaning functions from `preprocessing/cleaning.py`,
so there's only one definition of "what counts as clean text" in the
whole project.

## Installation

From the **repository root** (not inside `ai/`):

```bash
python -m venv .venv
source .venv/bin/activate        # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r ai/requirements.txt
cp .env.example .env             # Windows: copy .env.example .env
```

`.env` is optional for Milestone 1 — nothing here actually reads
`OPENAI_API_KEY` etc. yet — but setting it up now means Milestone 2
won't need a new setup step.

## Dataset

Kaggle: [Customer Support Ticket Dataset by Suraj](https://www.kaggle.com/datasets/suraj520/customer-support-ticket-dataset)

Place the download at `ai/data/raw/customer_support_tickets.csv`.

> **Assumption:** `ai/config/config.py`'s `COLUMN_MAP` reflects this
> dataset's published headers at the time this project was written —
> verify with `dataset_analysis.py` below and edit `COLUMN_MAP` if
> your file differs.

**Don't have the Kaggle file yet, or just want to test the code?**
Every script below accepts `--sample` to use the small, clearly
**synthetic** `ai/data/sample/sample_feedback.csv` (9 rows, fake
names/emails) instead. Never quote its numbers as real results.

## Running

All commands from the **repository root**:

```bash
# 1. Inspect the raw data first — changes nothing
python -m ai.analysis.dataset_analysis            # real Kaggle CSV
python -m ai.analysis.dataset_analysis --sample    # bundled sample

# 2. Clean it and generate the quality report
python -m ai.pipeline.feedback_pipeline
python -m ai.pipeline.feedback_pipeline --sample

# 3. Run the tests
pytest ai/tests/ -v
```

## Expected output

> Illustrative example from the bundled sample file — **not real
> Kaggle numbers**. Real numbers print automatically when you run
> against the actual dataset.

```
===== DATA QUALITY REPORT (Milestone 1) =====
Original records          : 9
Invalid/unusable removed  : 3
Exact duplicates removed  : 1
Description dupes removed : 1
Final records             : 4
```

## Data cleaning steps

1. **Load & normalize columns** via `config.COLUMN_MAP` — Kaggle's raw
   headers are converted to our stable internal names (`feedback_id`,
   `description`, ...) immediately; nothing downstream ever sees the
   raw Kaggle names.
2. **Select only normalized/useful columns** (`config.USEFUL_COLUMNS`)
   — identity fields (customer name/email) are dropped early.
3. **Clean text** (`subject`, `description`): collapse whitespace,
   strip control characters. Punctuation/casing kept — they carry
   sentiment/urgency signal future NLP steps may need.
4. **Drop rows with no usable core text**: dropped only if both
   `subject` and `description` are empty, or `description` is under
   15 characters (`config.MIN_DESCRIPTION_LENGTH`) — a strong signal
   of placeholder junk like `"na"` rather than real feedback.
5. **Remove exact duplicate rows.**
6. **Remove duplicate descriptions** (same complaint, different ID) —
   toggle via `DEDUPLICATE_ON_DESCRIPTION` in `feedback_pipeline.py`.
7. **Fill non-critical missing metadata** (e.g. missing `priority`)
   with `"Unknown"` — never done for core text.
8. **Add empty `ai_analysis` placeholder fields** — always `None` in
   Milestone 1, never fabricated.

## Canonical schema

See `ai/schemas/feedback.py` (`FeedbackRecord`, `AIAnalysis`) — this
is the single source of truth, also documented with the full example
JSON in `../docs/AI_INTEGRATION.md` section 5.

Three layers, never mixed:
- **Raw** — whatever Kaggle calls a column. Only `config.COLUMN_MAP`
  and `analysis/dataset_analysis.py` reference these.
- **Normalized** — our stable names, used everywhere else.
- **AI-generated** — `sentiment`, `category`, `theme`, `pain_point`,
  `feature_opportunity`. Always `None` until Milestone 2+.

## Initial AI approach

| Approach | Difficulty | Explainability | Dev time | Cost | Verdict |
|---|---|---|---|---|---|
| Rule-based keyword matching | Low | Very high | Low | Free | Too rigid |
| Traditional ML (TF-IDF + classifier) | Medium | High | Medium | Free | Needs labeled data we don't have |
| Fine-tuned transformer | High | Medium | High | Needs GPU/data | Overkill for this timeline |
| LLM/API-based | Low–Medium | Medium | Low | Pay-per-call | Strong at open-ended extraction |
| Embeddings + clustering | Medium | Medium | Medium | Low | Great for discovering themes without labels |
| **Hybrid (embeddings+clustering for themes, LLM to summarize each cluster)** | Medium | Medium–High | Medium | Low–Medium | **Recommended** |

We don't have labeled training data and can't realistically train a
model from scratch in this timeline, so the hybrid approach — cluster
first (no labels needed), then use an LLM to turn each cluster into a
readable pain point / feature opportunity / sentiment — is the
practical choice.

## Future AI pipeline

```
Raw Feedback
    ↓
Data Cleaning              ← MILESTONE 1 (done)
    ↓
Text Preprocessing         ← MILESTONE 1 (done)
    ↓
Sentiment Analysis         ← Future
    ↓
Theme Extraction (embeddings + clustering)   ← Future
    ↓
Pain Point Identification (LLM summarization)  ← Future
    ↓
Feature Opportunity Detection  ← Future
    ↓
Feature Clustering → Prioritization → PRD/User Stories/Roadmap  ← Future
```

## Team integration diagram

```
                 React
                   |
                   ↓
              FastAPI
                   |
          ┌────────┴────────┐
          ↓                 ↓
     AI/Python           MongoDB
   (this module,              ↑
  services/feedback_          |
     analyzer.py)             |
          |                   |
          ↓                   |
   NLP / AI Processing        |
          |                   |
          ↓                   |
    Structured Result ────────┘
```

- **React**: displays feedback and (later) AI-generated insights. Never
  talks to this module directly.
- **FastAPI**: the only caller of `ai.services.feedback_analyzer.analyze_feedback()`.
  Owns validation, HTTP concerns, and writing to MongoDB.
- **AI module (this folder)**: pure processing — text in, structured
  dict out. No routing, no auth, no direct DB writes in Milestone 1.
- **MongoDB**: stores the canonical document shape from `schemas/feedback.py`.

## File ownership

| Files | Owner |
|---|---|
| `ai/**` | AI teammate (you) |
| `backend/**` | Backend teammate |
| `frontend/**` | Frontend teammate |
| `database/**` | Database teammate |
| Root `README.md`, `.env.example`, `.gitignore`, `docs/**` | **Shared** — coordinate before editing |

## What I need from the Backend teammate / Database teammate / Frontend teammate

See `../docs/AI_INTEGRATION.md` sections 7, 8, and 9 for the exact
checklists — not duplicated here to avoid the two docs drifting apart.

## Limitations

- No AI model implemented yet — all five `ai_analysis` fields are
  always `None`. This is by design for Milestone 1, not a bug.
- Duplicate-description detection is exact-text-match only; won't
  catch differently-worded duplicates (planned for Milestone 2 via
  embeddings).
- `MIN_DESCRIPTION_LENGTH` is a simple heuristic, not learned from
  data — reasonable for now, worth revisiting on the real dataset.
- Environment variables for Milestone 2 (`AI_MODEL`, `OPENAI_API_KEY`,
  `GEMINI_API_KEY`) are wired into `config.py` but not used by any
  code yet.

## Milestone 1 demo sequence

1. Show the raw CSV (or the sample file) opened in Excel/Sheets.
2. Run `python -m ai.analysis.dataset_analysis --sample` — show
   columns, dtypes, missing values, duplicates.
3. Point out excluded identity columns and why.
4. Run `python -m ai.pipeline.feedback_pipeline --sample` — show the
   before/after quality report and the `INFO` log lines.
5. Open `ai/data/processed/cleaned_feedback.csv` — show cleaned rows
   plus the five empty `ai_analysis`-equivalent columns.
6. Open `data_quality_report.json` — real, measured numbers.
7. Show the schema (`schemas/feedback.py`) — raw vs. normalized vs.
   AI-generated layers.
8. Show the AI pipeline diagram above — done vs. future.
9. Run `pytest ai/tests/ -v` — 20 tests, no MongoDB/FastAPI/React needed.
10. Show `services/feedback_analyzer.py` and call `analyze_feedback()`
    live in a Python shell — this is exactly what the backend will do.
11. Walk through `docs/AI_INTEGRATION.md` — the actual handoff contract.

## Viva explanation (simple language)

"For Milestone 1, I picked a public Kaggle dataset of customer support
tickets and cleaned it — removed duplicates, handled missing values,
and standardized the text without deleting real customer words. But
the bigger change this round was making my code ready for the rest of
the team: I built one single function, `analyze_feedback()`, that the
backend teammate can call without knowing anything about pandas or
file paths — they just send text in and get a structured result back.
I also defined one shared schema for what a 'feedback record' looks
like, so the AI module, the backend, and the database all agree on the
same field names. Nothing about the AI analysis itself is faked — the
sentiment/theme/pain-point fields exist in the schema but stay empty
until Milestone 2 actually implements that logic."

## Future milestones

- **Milestone 2**: implement sentiment analysis and embedding-based
  theme clustering; use an LLM to summarize clusters into pain points
  and feature opportunities; `analyze_feedback()`'s output grows to
  include these fields (contract already documented).
- **Milestone 3**: feature clustering and prioritization logic.
- **Milestone 4**: PRD generation, user story generation, roadmap
  generation, and the conversational product-intelligence assistant.
