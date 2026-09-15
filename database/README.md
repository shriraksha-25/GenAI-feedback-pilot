# database/

Owned by the database teammate. Not yet populated.

See ../docs/AI_INTEGRATION.md section 5 ("AI <-> MongoDB contract")
for the canonical feedback document shape the AI module expects to
eventually populate, and section 8 for a database handoff checklist.

## Milestone 2 database support

Milestone 2 extends each feedback document with AI-generated analysis:

- AI processing status
- Theme and sentiment
- Customer pain point
- Feature opportunity and category
- Feature-opportunity group and cluster ID
- Confidence scores
- Analysis timestamps and errors

### Save and retrieve analysis

```python
from database.feedback_repository import (
    get_analyzed_feedback,
    get_feedback_by_id,
    save_feedback_analysis,
)

await save_feedback_analysis(feedback_id, analysis_result)
feedback = await get_feedback_by_id(feedback_id)
records = await get_analyzed_feedback(workspace_id)
```

The dictionary returned by `ai.services.feedback_analyzer.analyze_feedback()`
can be passed directly to `save_feedback_analysis()`.

### Dashboard and trend queries

```python
from database.dashboard_queries import (
    get_dashboard_insights,
    get_feedback_trends,
)

insights = await get_dashboard_insights(workspace_id)
trends = await get_feedback_trends(workspace_id, days=30)
```

### Verification

After configuring the local `.env`, run:

```powershell
python -m database.init_db
python -m database.verify_milestone2
```

The verification script creates a temporary record, tests all Milestone 2
operations, and removes the temporary record afterward.