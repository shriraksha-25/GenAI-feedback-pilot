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

## 4. What you'll get back — Milestone 2+ (planned, NOT implemented yet)

```json
{
  "feedback_id": "123",
  "cleaned_text": "Payment failed during checkout",
  "status": "processed",
  "sentiment": "negative",
  "category": "payment",
  "theme": "payment failure",
  "pain_point": "customers cannot complete payments",
  "feature_opportunity": "improved payment recovery"
}
```

Do not build frontend/backend logic today that assumes `sentiment`,
`category`, `theme`, `pain_point`, or `feature_opportunity` exist in
the response yet — they don't. When Milestone 2 adds them, this
document will be updated first.

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
  "subject": "Payment failed",
  "description": "Payment failed during checkout",
  "priority": "High",
  "status": "Open",
  "channel": "Email",
  "customer_satisfaction": null,
  "created_at": "2024-01-05",
  "ai_analysis": {
    "sentiment": null,
    "category": null,
    "theme": null,
    "pain_point": null,
    "feature_opportunity": null
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
  through whatever the AI module returns (once Milestone 2 populates
  them).
- All `ai_analysis` fields are `null` until Milestone 2+.

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
      `ai_analysis`, may be null).
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

Fields the frontend can eventually display once Milestone 2 populates
them (currently always `null`, so build any UI for these as
"not yet available" / hidden until implemented):

```
sentiment, category, theme, pain_point, feature_opportunity
```

- [ ] Let me know if there's a specific display format you'd want
      these in (e.g. sentiment as a label vs. a numeric score) — it
      may influence how Milestone 2 formats the output.

## 10. Known integration risks / things to double-check once real files exist

- I have not seen actual frontend/backend/database code yet — this
  document defines the *intended* contract, not a tested integration.
  Once those files exist, re-verify imports, working directory
  assumptions, and the exact request/response JSON against this doc.
- If the backend's environment installs dependencies from a different
  `requirements.txt` (e.g. a root-level combined file) rather than
  `ai/requirements.txt` directly, make sure `pandas`, `numpy`, and
  `python-dotenv` are included there too.
