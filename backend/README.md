# Backend – FastAPI

Backend service for the AI Product Manager Copilot.

## Setup

Create/activate the backend virtual environment and install dependencies:

```powershell
.\backend\venv\Scripts\python.exe -m pip install -r backend\requirements.txt
```

## Run the Backend

Run from the repository root:

```powershell
.\backend\venv\Scripts\python.exe -m uvicorn backend.main:app --reload
```

Backend URL:

```text
http://127.0.0.1:8000
```

Swagger API Documentation:

```text
http://127.0.0.1:8000/docs
```

## Main APIs

### Feedback

```text
POST /feedback/
```

Receives customer feedback, sends it to the AI module for analysis, and stores the processed result in MongoDB when the database is available.

### Product Insights

```text
GET /insights/summary
GET /insights/sentiments
GET /insights/categories
GET /insights/themes
GET /insights/pain-points
GET /insights/feature-requests
GET /insights/trends
```

These endpoints provide aggregated product insights for the frontend dashboard.

## Health Check

```text
GET /health
```

Example:

```json
{
  "service": "backend",
  "status": "healthy",
  "database_status": "connected"
}
```

If MongoDB is temporarily unavailable, the backend can still start and reports:

```json
{
  "service": "backend",
  "status": "healthy",
  "database_status": "unavailable"
}
```

## Milestone 2 Integration

The backend is prepared to consume AI-generated fields:

* sentiment
* category
* theme
* pain point
* feature opportunity

The actual values will be populated when the CrewAI agentic layer is integrated.
