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

## Milestone 4 Database Support

Milestone 4 extends the database with roadmap planning, executive reporting,
what-if simulation, and AI quality monitoring.

### Supported workflow

Feedback → AI Insights → Feature Opportunity → Priority Score → Roadmap →
Milestones → Executive Summary → PDF Report

### Collections

- `roadmaps`: Versioned product roadmaps containing milestones, scheduled features, capacity, assumptions, risks, and dependencies.
- `executive_summaries`: Versioned product strategy and executive summaries.
- `report_metadata`: PDF report generation status, storage information, and download metadata.
- `roadmap_simulations`: What-if scenarios based on changes to capacity, feature schedules, and planning assumptions.
- `ai_quality_evaluations`: AI output validation, relevance, completeness, evidence coverage, warnings, and response-time measurements.

### Important capabilities

- Creates and retrieves workspace-specific roadmaps.
- Preserves immutable roadmap version history.
- Supports AI Draft, Under Review, Approved, and Rejected states.
- Stores milestones, feature sequencing, effort, impact, risks, and dependencies.
- Prevents invalid, unknown, self-referencing, and circular feature dependencies.
- Connects roadmap recommendations to features and source feedback evidence.
- Supports evidence-linked roadmap views.
- Stores executive-summary versions without overwriting older versions.
- Tracks PDF report generation status and metadata without storing credentials.
- Supports What-If Roadmap Simulator scenarios without replacing the current baseline roadmap.
- Records AI quality, completeness, relevance, evidence coverage, missing information, and response time.
- Enforces workspace-level data separation in repository and query operations.

### Milestone 4 files

- `milestone4_models.py`: Roadmap, milestone, report, simulation, and AI-quality models.
- `roadmap_repository.py`: Roadmap creation, versioning, retrieval, review status, and integrity validation.
- `executive_summary_repository.py`: Executive-summary storage and version history.
- `report_repository.py`: PDF report metadata and generation-status lifecycle.
- `roadmap_queries.py`: Evidence-linked roadmap, dashboard, and product-strategy queries.
- `simulation_repository.py`: What-if roadmap scenario persistence.
- `quality_repository.py`: AI quality evaluation and trust-dashboard queries.
- `sample_milestone4_data.py`: Realistic Milestone 4 integration-test data.
- `verify_milestone4.py`: Automated Milestone 4 database workflow verification.
- `indexes.py`: MongoDB indexes supporting all project milestones.

### Main relationships

```text
Workspace
 ├── Feedback
 ├── Features
 │    ├── Feature Evidence
 │    └── Priority Scores
 ├── Roadmaps
 │    ├── Milestones
 │    ├── Scheduled Features
 │    └── Dependencies
 ├── Executive Summaries
 ├── Report Metadata
 ├── Roadmap Simulations
 └── AI Quality Evaluations
```

Every Milestone 4 document includes a `workspace_id` to preserve workspace-level
data separation. Roadmaps, executive summaries, and other generated artifacts
use stable identifiers and version numbers to preserve their complete history.

PDF files are generated by the backend. The database stores only report metadata,
generation status, checksum, storage location, timestamps, and error details.

### Verification

After configuring the local `.env` file, activate the virtual environment and run:

```powershell
python -m database.init_db
python -m database.verify_milestone4
```

The verification script tests:

- Roadmap creation and retrieval
- Roadmap version history
- Milestone and dependency integrity
- Executive-summary versions
- PDF report metadata lifecycle
- Evidence-linked roadmap queries
- Roadmap dashboard metrics
- What-if simulation persistence
- AI quality and trust metrics
- Workspace-level data isolation

All temporary verification records are removed after the test.