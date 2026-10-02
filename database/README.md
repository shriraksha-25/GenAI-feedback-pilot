# MongoDB Database Module

This module stores customer feedback, AI analysis, product requirements,
prioritization results, version history and Product Intelligence Assistant
conversations.

See `../docs/AI_INTEGRATION.md` for the AI-to-MongoDB data contract.

## Milestone 2 Database Support

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

The dictionary returned by
`ai.services.feedback_analyzer.analyze_feedback()` can be passed directly
to `save_feedback_analysis()`.

### Dashboard and trend queries

```python
from database.dashboard_queries import (
    get_dashboard_insights,
    get_feedback_trends,
)

insights = await get_dashboard_insights(workspace_id)
trends = await get_feedback_trends(workspace_id, days=30)
```

### Milestone 2 verification

After configuring the local `.env`, run:

```powershell
python -m database.init_db
python -m database.verify_milestone2
```

The verification script creates a temporary record, tests the Milestone 2
operations and removes the temporary record afterward.

## Milestone 3 Database Support

Milestone 3 extends the database from feedback analysis into product
requirements planning.

### Supported workflow

Feedback → AI Insight → Feature Opportunity → Priority Score → PRD →
User Stories and Acceptance Criteria → PM Review → Product Intelligence
Assistant

### Collections

- `features`: Feature opportunities created from analyzed feedback.
- `feature_evidence`: Links features to supporting customer feedback.
- `priority_configurations`: Configurable prioritization settings.
- `priority_scores`: RICE inputs, calculated scores and explanations.
- `prds`: Versioned Product Requirements Documents.
- `user_stories`: Versioned user stories with acceptance criteria.
- `conversations`: Product Intelligence Assistant conversations.
- `chat_messages`: Individual user, assistant and system messages.
- `workflow_events`: Audit history for workflow and status changes.

### Important capabilities

- Maintains feedback-to-requirement traceability.
- Stores RICE inputs separately from calculated scores.
- Supports configurable scoring weights.
- Preserves all PRD and user-story versions.
- Stores AI drafts, review status and approval information.
- Stores acceptance criteria using Given-When-Then format.
- Maintains Product Intelligence Assistant conversation history.
- Preserves source feedback IDs for evidence-based AI responses.
- Records workflow changes for auditing.

### Milestone 3 files

- `milestone3_models.py`: Milestone 3 Pydantic models.
- `feature_repository.py`: Feature and evidence persistence.
- `priority_repository.py`: RICE calculation and priority storage.
- `requirements_repository.py`: PRD and user-story version storage.
- `conversation_repository.py`: Conversation and message history.
- `traceability_queries.py`: End-to-end traceability queries.
- `verify_milestone3.py`: Automated database workflow verification.
- `indexes.py`: MongoDB indexes for all milestones.

### Milestone 3 verification

Activate the virtual environment and run:

```powershell
python -m database.init_db
python -m database.verify_milestone3
```

Expected result:

```text
Milestone 3 database verification successful
Feature and feedback evidence: successful
RICE prioritization: successful
PRD version history: successful
User stories and acceptance criteria: successful
Conversation history: successful
End-to-end traceability: successful
Temporary Milestone 3 test records removed
```