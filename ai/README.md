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
├── agents/                  # ★ NEW — Milestone 2 CrewAI agentic layer
│   ├── schemas.py           # per-agent structured output (pydantic, required by crewai)
│   ├── llm.py                # GenAI provider selection (OpenAI/Gemini), from env vars only
│   └── crew.py                # the 3 agents + tasks + crew orchestration
├── preprocessing/
│   └── cleaning.py          # small, testable cleaning functions
├── pipeline/
│   └── feedback_pipeline.py # batch: clean a whole CSV, offline/dev tool
├── services/
│   ├── feedback_analyzer.py # ★ PUBLIC INTERFACE — what the backend imports
│   └── feature_clustering.py # ★ NEW — batch grouping of similar feature requests
├── analysis/
│   └── dataset_analysis.py  # look-only dataset inspection
├── data/
│   ├── raw/       # put the real Kaggle CSV here (gitignored)
│   ├── processed/ # pipeline output lands here (gitignored)
│   └── sample/    # small SYNTHETIC sample_feedback.csv (committed)
├── tests/
│   ├── test_preprocessing.py
│   ├── test_feedback_analyzer.py       # Milestone 1: text cleaning/validation only
│   ├── test_feedback_analyzer_ai.py    # Milestone 2: AI-augmentation behavior
│   ├── test_pipeline.py
│   ├── test_agent_schemas.py           # Milestone 2
│   ├── test_crew.py                    # Milestone 2
│   └── test_feature_clustering.py      # Milestone 2
└── requirements.txt
```

**Why this shape?** `services/` is the only folder a teammate outside
this module should ever import from — it's the "front door." Everything
else (`preprocessing`, `pipeline`, `analysis`, `config`, `agents`) is an
implementation detail `services/` builds on, but none of it is exposed
directly. `agents/` follows the same pattern one level in: only
`services/feedback_analyzer.py` and `services/feature_clustering.py`
import from it — the backend never imports `ai.agents` directly.

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
- **AI-generated** — `sentiment`, `category` (always `None` — not in
  scope, see below), `theme`, `pain_point`, `feature_opportunity`,
  `feature_category`, `feature_opportunity_group`, `confidence`
  (populated as of Milestone 2 — see "Milestone 2" section below for
  exactly when each is populated vs. `None`).

## Initial AI approach (Milestone 1 analysis)

| Approach | Difficulty | Explainability | Dev time | Cost | Verdict |
|---|---|---|---|---|---|
| Rule-based keyword matching | Low | Very high | Low | Free | Too rigid |
| Traditional ML (TF-IDF + classifier) | Medium | High | Medium | Free | Needs labeled data we don't have |
| Fine-tuned transformer | High | Medium | High | Needs GPU/data | Overkill for this timeline |
| LLM/API-based | Low–Medium | Medium | Low | Pay-per-call | Strong at open-ended extraction |
| Embeddings + clustering | Medium | Medium | Medium | Low | Great for discovering themes without labels |
| **Hybrid (LLM agents per-record, embeddings+clustering for cross-record grouping)** | Medium | Medium–High | Medium | Low–Medium | **Chosen — see Milestone 2 below** |

We don't have labeled training data and can't realistically train a
model from scratch in this timeline, so the hybrid approach — LLM
agents extract structured signal from each piece of feedback
individually, then embeddings + clustering group similar feature
requests across many records — is what Milestone 2 actually
implements below.

## Milestone 2 — AI/GenAI Agentic Layer (implemented)

Three CrewAI agents, run sequentially per piece of feedback, each
producing a validated structured (pydantic) output — see
`ai/agents/crew.py` and `ai/agents/schemas.py`:

| Agent | Role | Output |
|---|---|---|
| **Theme Extraction Agent** | Identify the main topic | `theme` (short label) + `confidence` |
| **Customer Pain Point Agent** | State the concrete problem/friction | `pain_point` (one sentence) + `confidence` |
| **Feature Request Agent** | Detect + categorize feature requests, honestly reporting when there isn't one | `feature_request`, `feature_category`, `confidence` |

**Feature request clustering** (grouping "Add UPI payments" / "Support
Google Pay" / "Give us more payment options" into one opportunity) is
a **separate batch function**, not a fourth agent — see
`ai/services/feature_clustering.py` and
`../docs/AI_INTEGRATION.md` section 4b for why and how to call it.

**GenAI provider**: configurable via `OPENAI_API_KEY` / `GEMINI_API_KEY`
in `.env` (see "Milestone 2 setup" below) — recommended is Gemini
(free tier), OpenAI works as a drop-in alternative. Neither key is
hardcoded anywhere; `ai/agents/llm.py` is the only place provider
selection happens.

**Sentiment analysis and generic `category` classification are
explicitly NOT part of this Milestone 2 scope** (per the project
brief — only the three agents above). Both schema fields remain
`None`; nothing in this codebase invents a value for them.

### Milestone 2 setup

1. Get a free Gemini API key: https://aistudio.google.com/apikey
   (or use an existing OpenAI key if you have one).
2. `cp .env.example .env` (Windows: `copy .env.example .env`) if you
   haven't already, then fill in `GEMINI_API_KEY=...` (or
   `OPENAI_API_KEY=...`).
3. Install the Milestone 2 dependencies (see `ai/requirements.txt`):
   ```bash
   pip install -r ai/requirements.txt
   pip install "crewai[google-genai]"   # only if using Gemini
   ```
4. Try a live end-to-end call from the repo root:
   ```bash
   python -c "from ai.services.feedback_analyzer import analyze_feedback; import json; print(json.dumps(analyze_feedback(text='The app keeps crashing whenever I try to upload a document.'), indent=2))"
   ```
   Expect `ai_status: "completed"` with real `theme`/`pain_point`
   values. If you see `ai_status: "not_configured"`, double-check your
   `.env`. If you see `ai_status: "failed"` with a **404 NOT_FOUND /
   "model ... is not found"** error, the configured Gemini model
   version has been retired (Google does this on a rolling basis) —
   list the models your own key currently supports and update
   `AI_MODEL` in `.env`:
   ```bash
   python -c "from google import genai; import os; from dotenv import load_dotenv; load_dotenv(); client = genai.Client(api_key=os.environ['GEMINI_API_KEY']); [print(m.name) for m in client.models.list() if 'generateContent' in (m.supported_actions or [])]"
   ```

## Future AI pipeline

```
Raw Feedback
    ↓
Data Cleaning              ← MILESTONE 1 (done)
    ↓
Text Preprocessing         ← MILESTONE 1 (done)
    ↓
Theme Extraction (CrewAI agent)         ← MILESTONE 2 (done)
    ↓
Pain Point Identification (CrewAI agent) ← MILESTONE 2 (done)
    ↓
Feature Request Detection (CrewAI agent) ← MILESTONE 2 (done)
    ↓
Feature Request Clustering (embeddings)  ← MILESTONE 2 (done, batch)
    ↓
Sentiment Analysis         ← Future (different milestone/owner)
    ↓
Prioritization → PRD/User Stories/Roadmap  ← Future
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

- Sentiment analysis and generic `category` classification are not
  part of this Milestone 2 AI scope — both fields stay `None`. This is
  by design (see the project brief), not a bug.
- Duplicate-description detection (Milestone 1) is exact-text-match
  only; won't catch differently-worded duplicate tickets.
- `MIN_DESCRIPTION_LENGTH` is a simple heuristic, not learned from
  data — reasonable for now, worth revisiting on the real dataset.
- Feature request clustering's real-embeddings path was built and unit
  tested with mocked embedding calls, but **not exercised against a
  live OpenAI/Gemini embeddings call** in this development environment
  (no network access to those hosts here) — run the Milestone 2 setup
  smoke test above with a real key before demoing clustering live.
  The TF-IDF fallback path (used automatically when no provider is
  configured) was fully tested for real.
- Live CrewAI agent calls (theme/pain-point/feature-request extraction)
  were built against the real installed `crewai` API and are unit
  tested via dependency-injected fake crews (`ai/tests/test_crew.py`),
  but likewise not exercised end-to-end against a live API in this
  environment — see docs/AI_INTEGRATION.md section 10.
- CrewAI's own dependency footprint is fairly large (it pulls in
  several sub-dependencies beyond just the LLM SDK). This was accepted
  as the cost of using the specifically-requested CrewAI framework;
  `sentence-transformers`/PyTorch was deliberately avoided for
  clustering to keep the *additional* footprint smaller.

## Milestone 1 demo sequence

1. Show the raw CSV (or the sample file) opened in Excel/Sheets.
2. Run `python -m ai.analysis.dataset_analysis --sample` — show
   columns, dtypes, missing values, duplicates.
3. Point out excluded identity columns and why.
4. Run `python -m ai.pipeline.feedback_pipeline --sample` — show the
   before/after quality report and the `INFO` log lines.
5. Open `ai/data/processed/cleaned_feedback.csv` — show cleaned rows
   plus the empty `ai_analysis`-equivalent columns.
6. Open `data_quality_report.json` — real, measured numbers.
7. Show the schema (`schemas/feedback.py`) — raw vs. normalized vs.
   AI-generated layers.

## Milestone 2 demo sequence

1. Show `ai/agents/crew.py` — the three agents, their roles/goals, and
   how the crew runs them sequentially.
2. Run the live smoke test from "Milestone 2 setup" above — show a
   real `theme`/`pain_point` result coming back for a sample complaint.
3. Run it again with feedback that contains a feature request (e.g.
   *"I wish I could save my frequently used reports"*) — show
   `feature_opportunity` and `feature_category` populated.
4. Run it a third time with pure positive feedback with no request —
   show `feature_opportunity: null` and explain the agent is being
   honest, not failing.
5. Show `ai/services/feature_clustering.py` grouping the payment
   example (`Add UPI payments` / `Support Google Pay` / `Give us more
   payment options`) into one opportunity.
6. Temporarily unset both API keys and re-run step 2 — show
   `ai_status: "not_configured"` with a clear message, proving nothing
   is silently faked when unconfigured.
7. Run `pytest ai/tests/ -v` — 46 tests, including all original
   Milestone 1 tests still passing unmodified, no MongoDB/FastAPI/React
   or live API key needed for the full suite.
8. Walk through `docs/AI_INTEGRATION.md` sections 4 and 4b — the
   actual backend handoff contract.

## Viva explanation (simple language)

"Milestone 1 was about cleaning the data and designing the schema.
Milestone 2 is where the actual AI comes in: I built three CrewAI
agents that each read a piece of customer feedback and pull out one
specific thing — a Theme Extraction Agent finds the topic, a Pain
Point Agent states the real problem in plain language, and a Feature
Request Agent notices when the customer is asking for something new,
categorizes it, and honestly says 'no request here' when there isn't
one rather than inventing one. All three run through CrewAI as a
sequential crew and return structured, validated data instead of
free-form paragraphs. I also built a separate clustering step that
groups similar feature requests together — like 'add UPI payments' and
'support Google Pay' both being about payment options — using semantic
embeddings from whichever AI provider we've configured. The backend
still only needs to call one function, `analyze_feedback()`, exactly
like before; it just gets richer results now. And if no API key is
configured, or the AI call fails, the system says so honestly instead
of making something up."

## Future milestones

- **Milestone 2 (this milestone)**: three CrewAI agents (Theme, Pain
  Point, Feature Request) plus feature-request clustering —
  implemented, see "Milestone 2" section above.
- **Milestone 3**: sentiment analysis (separate scope/owner per the
  project brief), feature prioritization logic, business impact
  analysis.
- **Milestone 4**: PRD generation, user story generation, roadmap
  generation, and the conversational product-intelligence assistant.
