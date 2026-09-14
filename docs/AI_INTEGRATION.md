# AI Module Integration Guide

This document is for the **backend (FastAPI) teammate**. It explains
exactly what to import, what to send, and what you'll get back from
the AI module. You do not need to know pandas, file paths, or
anything about how cleaning works internally.

## 1. What to import

```python
from ai.services.feedback_analyzer import analyze_feedback
```

This works as long as your FastAPI app runs from the repository root
(so `ai/` is importable as a top-level package) and
`ai/requirements.txt` is installed in the same environment as your
FastAPI app (or a shared root `requirements.txt` that includes it —
worth agreeing on as a team).

## 2. How to call it

```python
result = analyze_feedback(
    text="Payment failed during checkout",
    feedback_id="123",              # optional — your own ID, echoed back
    metadata={"product": "Mobile App", "source": "support_ticket"},  # optional
)
```

- `text` (**required**, `str`) — the raw feedback/complaint text.
- `feedback_id` (optional, `str`) — your own identifier (e.g. a Mongo
  `_id` or a form submission ID). Echoed back unchanged so you can
  match the result to your own record. If you don't pass one, the
  result's `feedback_id` will be `None`.
- `metadata` (optional, `dict`) — extra context. Not used by any
  Milestone 1 logic, accepted now so this signature won't need to
  change when Milestone 2 starts using it.

## 3. What you get back — Milestone 1 (implemented now)

```json
{
  "feedback_id": "123",
  "cleaned_text": "Payment failed during checkout",
  "status": "processed"
}
```

If the input was empty, not a string, or too short to be real
feedback:

```json
{
  "feedback_id": "123",
  "cleaned_text": "",
  "status": "rejected",
  "error": "text is missing, empty, or not a string"
}
```

**`analyze_feedback()` never raises an exception for bad input** — it
always returns a dict. Check `result["status"]` (`"processed"` or
`"rejected"`); only wrap the call in `try/except` to guard against a
genuine internal bug, not for input validation.

## 4. What you get back — Milestone 2 (implemented now)

```json
{
  "feedback_id": "123",
  "cleaned_text": "The app keeps crashing whenever I try to upload a document.",
  "status": "processed",
  "ai_status": "completed",
  "theme": "App Stability",
  "pain_point": "Customers are unable to upload documents because the app crashes.",
  "feature_opportunity": null,
  "feature_category": null,
  "confidence": {
    "theme": 0.9,
    "pain_point": 0.92,
    "feature_opportunity": 0.6
  },
  "sentiment": null,
  "category": null
}
```

Field-by-field:

- `status` — **unchanged meaning from Milestone 1**: was the input text itself usable? `"processed"` or `"rejected"`. AI analysis never runs at all for rejected text.
- `ai_status` — **new in Milestone 2**, only present when `status == "processed"`. One of:
  - `"completed"` — all three agents ran successfully; `theme`, `pain_point`, `feature_opportunity`/`feature_category`, and `confidence` are populated (any of them may still legitimately be `null` — e.g. `feature_opportunity` is `null` whenever the feedback contained no feature request at all, not as an error).
  - `"not_configured"` — no `OPENAI_API_KEY` or `GEMINI_API_KEY` is set. `theme`/`pain_point`/`feature_opportunity`/`confidence` are all `null`. An `ai_error` string explains what to configure.
  - `"failed"` — a provider/LLM error occurred (rate limit, network error, malformed model response, etc.). Same all-`null` shape as `not_configured`, with `ai_error` containing the exception message. **Nothing is ever fabricated when analysis doesn't succeed** — treat `theme`/`pain_point`/`feature_opportunity` as trustworthy only when `ai_status == "completed"`.
- `theme` — short topic label from the Theme Extraction Agent (e.g. `"App Stability"`).
- `pain_point` — one-sentence description of the customer's actual problem, from the Pain Point Agent.
- `feature_opportunity` — the extracted feature request text, from the Feature Request Agent. **`null` whenever the feedback contained no feature request** (a pure bug report, a compliment, etc.) — this is a normal, honest result, not a failure.
- `feature_category` — broad category for the feature request (e.g. `"Reporting"`, `"Payments"`). `null` whenever `feature_opportunity` is `null`.
- `confidence` — per-field model confidence (0.0-1.0) for `theme`, `pain_point`, and `feature_opportunity` respectively. All `null` unless `ai_status == "completed"`.
- `sentiment`, `category` — **always `null`**. These two fields were reserved in the Milestone 1 schema but are explicitly **not** part of the Milestone 2 AI/GenAI scope (three agents only: Theme, Pain Point, Feature Request) — nothing in this codebase invents a value for them. If a future milestone implements sentiment analysis, this document will be updated first.

If the input text itself was invalid, the shape is unchanged from Milestone 1:

```json
{
  "feedback_id": "123",
  "cleaned_text": "",
  "status": "rejected",
  "error": "text is missing, empty, or not a string"
}
```

**`analyze_feedback()` still never raises an exception** — for bad input OR for AI-analysis failures. Check `status` first (text validity), then `ai_status` if you need to know whether AI fields are trustworthy.

## 4b. Feature request clustering (batch, separate from analyze_feedback)

`analyze_feedback()` only ever sees one piece of feedback at a time, so it cannot group similar feature requests together — that requires comparing many requests against each other. For that, call
`ai.services.feature_clustering.cluster_feature_requests()` separately, once you've collected several `analyze_feedback()` results with non-null `feature_opportunity`:

```python
from ai.services.feature_clustering import cluster_feature_requests

items = [
    {"feedback_id": "1", "feature_request": "Add UPI payments"},
    {"feedback_id": "2", "feature_request": "Support Google Pay"},
    {"feedback_id": "3", "feature_request": "Give us more payment options"},
]
grouped = cluster_feature_requests(items)
# -> each item gets "feature_opportunity_group" (shared label for the cluster)
#    and "cluster_id" (integer, stable within this call only)
```

This is a **batch/offline operation** (like `pipeline/feedback_pipeline.py`), not something called per-request in the main feedback flow. A reasonable place to call it: periodically, or whenever the PM wants an updated view of grouped feature opportunities — that scheduling decision belongs to the backend team.

Clustering uses real semantic embeddings from whichever GenAI provider is already configured (OpenAI or Gemini — no new API key needed), because feature requests like "Add UPI payments" and "Support Google Pay" share almost no vocabulary and cannot be grouped by keyword overlap alone. If no provider is configured, it automatically falls back to local TF-IDF similarity (works offline, groups lexically-similar requests, may miss fully cross-vocabulary paraphrases).

## 5. AI ↔ MongoDB contract (canonical document shape)

This is the single source of truth for what one feedback record looks
like in the database — defined in `ai/schemas/feedback.py`
(`FeedbackRecord` / `AIAnalysis`):

```json
{
  "feedback_id": "123",
  "source": "support_ticket",
  "product": "Mobile App",
  "ticket_type": "Technical issue",
  "subject": "Can't upload documents",
  "description": "The app keeps crashing whenever I try to upload a document.",
  "priority": "High",
  "status": "Open",
  "channel": "Email",
  "customer_satisfaction": null,
  "created_at": "2024-01-05",
  "ai_analysis": {
    "sentiment": null,
    "category": null,
    "theme": "App Stability",
    "pain_point": "Customers are unable to upload documents because the app crashes.",
    "feature_opportunity": null,
    "feature_category": null,
    "feature_opportunity_group": null,
    "confidence": {
      "theme": 0.9,
      "pain_point": 0.92,
      "feature_opportunity": 0.6
    }
  }
}
```

- **Top-level fields** (`feedback_id` through `created_at`): raw/normalized
  facts about the feedback. Populated either by the AI module (when
  batch-loading the Kaggle dataset — see `ai/pipeline/feedback_pipeline.py`)
  or by the backend (when a real user submits feedback through the
  API — you'd typically build this dict yourself from the request,
  possibly calling `analyze_feedback()` first to get `cleaned_text`).
- **`ai_analysis`**: owned by the AI module. Treat it as read-only —
  the backend should not compute or overwrite these values, only pass
  through whatever `analyze_feedback()` returns.
- `theme`, `pain_point`, `feature_opportunity`, `feature_category`,
  `confidence` — populated as of **Milestone 2** (see section 4 above
  for exactly when each is `null` vs. populated).
- `feature_opportunity_group` — **not** populated by `analyze_feedback()`
  (which only ever sees one record at a time). It's populated
  separately, in batch, by `ai.services.feature_clustering.cluster_feature_requests()`
  after grouping several records' `feature_opportunity` values — see
  section 4b below. Until that batch step runs (or for records with no
  feature request), this stays `null`.
- `sentiment`, `category` — **always `null` in this codebase**. Reserved
  in the schema but not part of the Milestone 2 AI scope (see section 4).

`ai/schemas/feedback.py` provides `build_mongo_document(record)` and
`empty_ai_analysis_dict()` as importable helpers if useful, but you're
also free to just build the equivalent dict yourself in FastAPI/Pydantic
— the JSON shape above is what matters, not which language builds it.

## 6. Suggested FastAPI endpoint shape (your call, not prescribed)

This is a **suggestion**, not something already built — you own the
actual FastAPI implementation:

```python
from fastapi import FastAPI
from ai.services.feedback_analyzer import analyze_feedback

app = FastAPI()

@app.post("/feedback")
def submit_feedback(payload: FeedbackIn):  # your own Pydantic model
    result = analyze_feedback(
        text=payload.text,
        feedback_id=payload.feedback_id,
        metadata={"product": payload.product, "source": payload.source},
    )
    if result["status"] == "rejected":
        # your call: 400 Bad Request, or store as-is with rejected status
        ...
    # ... build the full Mongo document (section 5) and save it
    return result
```

## 7. What I (AI teammate) need from the Backend teammate

- [ ] Confirm the repo will run FastAPI from the repository root (so
      `from ai...` imports resolve) — or tell me your actual working
      directory so I can adjust.
- [ ] Confirm whether you'll call `analyze_feedback()` synchronously
      in the request handler, or offload it to a background task/queue
      (matters if Milestone 2's LLM calls turn out to be slow).
  - [ ] Tell me which endpoint(s) will receive feedback, and their
      request JSON shape, so I can confirm it maps cleanly to
      `analyze_feedback()`'s parameters.
- [ ] Confirm who handles `status: "rejected"` results — reject the
      HTTP request, or store the rejected record anyway with that
      status?
- [ ] Confirm you'll store the AI module's output under `ai_analysis`
      exactly as returned, without transforming field names.

## 8. What I (AI teammate) need from the Database teammate

- [ ] Final MongoDB collection name for feedback records.
- [ ] Confirm the document schema in section 5 is acceptable, or tell
      me what needs to change.
- [ ] Confirm which fields are required vs. nullable at the DB level
      (my current assumption: only `feedback_id`, `source`, and
      `description` are required; everything else, including all of
      `ai_analysis`, may be null — including `feature_opportunity_group`,
      which stays null until the batch clustering step in section 4b
      has run for that record).
- [ ] Confirm ID strategy: is `feedback_id` the MongoDB `_id`, or a
      separate application-level field alongside an auto-generated
      `_id`? (My schema assumes the latter — `feedback_id` is a plain
      string field, not necessarily `_id`.)

## 9. What I (AI teammate) need from the Frontend teammate

The frontend does **not** call the AI module directly — it only ever
talks to FastAPI, which internally calls this module:

```
React → FastAPI → AI module
```

Fields the frontend can display **now** (Milestone 2, populated when
`ai_status == "completed"` — build UI that handles `null` gracefully
for the `"not_configured"`/`"failed"` cases too):

```
theme, pain_point, feature_opportunity, feature_category, confidence
```

Fields still always `null` (not part of Milestone 2 scope — build UI
for these as "not yet available" / hidden until a later milestone):

```
sentiment, category, feature_opportunity_group (until the batch
clustering step in section 4b has run)
```

- [ ] Let me know if there's a specific display format you'd want
      `confidence` in (e.g. a percentage vs. a raw 0-1 score, or a
      "high/medium/low" label) — easy to adjust in `feedback_analyzer.py`.

## 10. Known integration risks / things to double-check once real files exist

- I have not seen actual frontend/backend/database code yet — this
  document defines the *intended* contract, not a tested integration.
  Once those files exist, re-verify imports, working directory
  assumptions, and the exact request/response JSON against this doc.
- If the backend's environment installs dependencies from a different
  `requirements.txt` (e.g. a root-level combined file) rather than
  `ai/requirements.txt` directly, make sure `pandas`, `numpy`,
  `python-dotenv`, `crewai`, `pydantic`, and `scikit-learn` are
  included there too — see `ai/requirements.txt` for the full list and
  which GenAI provider extra (`crewai[google-genai]` for Gemini) to
  add based on which API key is configured.
- **Live LLM calls were not exercised end-to-end in this development
  environment** (network egress was restricted to package registries
  only, no access to `api.openai.com` / `generativelanguage.googleapis.com`).
  The CrewAI Agent/Task/Crew wiring was verified against the real
  installed `crewai` package's API (classes, fields, `output_pydantic`
  behavior), and all extraction/combination logic is tested with
  injected fake crews (see `ai/tests/test_crew.py`), but a real API
  key should be used to do one live end-to-end smoke test
  (`ai/README.md` "Milestone 2 setup" has the exact command) before
  considering this done. Please run that smoke test and let the team
  know the result.
