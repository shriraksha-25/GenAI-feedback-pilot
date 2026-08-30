# AI Product Manager Copilot

An AI assistant for Product Managers: it ingests customer feedback
(support tickets, reviews, feature requests, and eventually meeting
transcripts) and helps identify pain points, recurring themes, and
feature opportunities, then helps generate PRDs and user stories.

## Team & tech stack

| Component | Tech | Owner |
|---|---|---|
| Frontend | ReactJS | Frontend teammate |
| Backend | Python + FastAPI | Backend teammate |
| AI / NLP | Python | AI teammate (this repo's `ai/`) |
| Database | MongoDB | Database teammate |

## Repository structure

```
AI-Product-Manager-Copilot/
│
├── frontend/           # React app (frontend teammate)
├── backend/             # FastAPI app (backend teammate)
├── ai/                  # AI/Python module — see ai/README.md
├── database/             # MongoDB config/scripts, if needed
├── docs/
│   └── AI_INTEGRATION.md   # How the backend calls the AI module
│
├── .env.example
├── .gitignore
└── README.md            # (this file)
```

`frontend/`, `backend/`, and `database/` are placeholders here —
those teammates own and populate them independently. **This repo
currently only has the AI module fully built out; see `ai/README.md`
for everything about it.**

## Architecture (planned)

```
React
  ↓
FastAPI
  ↓
AI Python Module   (ai/services/feedback_analyzer.py)
  ↓
AI/NLP processing
  ↓
Structured result
  ↓
FastAPI
  ↓
MongoDB
  ↓
React
```

The AI module never talks to React, MongoDB, or handles
authentication/routing directly — FastAPI is the only thing that
calls it, and the only thing it returns is a plain JSON-compatible
dict. See `docs/AI_INTEGRATION.md` for the exact contract.

## Getting started

Each teammate works in their own folder. For the AI module
specifically, see **[ai/README.md](ai/README.md)** for full setup,
usage, and viva-prep material.

For how the backend should call the AI module, see
**[docs/AI_INTEGRATION.md](docs/AI_INTEGRATION.md)**.

## Environment variables

Copy `.env.example` to `.env` and fill in your own values. Never
commit `.env` — it's already in `.gitignore`.

## Shared files (coordinate before editing)

This root `README.md`, `.env.example`, `.gitignore`, and anything
under `docs/` affect the whole team — discuss changes with the team
before editing them, since they're easy to accidentally conflict on
across branches.
