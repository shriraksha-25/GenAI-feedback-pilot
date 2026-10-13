from typing import Any

from pymongo import ASCENDING, DESCENDING


async def create_indexes(database: Any) -> None:
    """Create indexes required by all project milestones."""

    # ---------------------------------------------------------
    # Existing users, feedback, workspaces and imports
    # ---------------------------------------------------------

    await database.users.create_index(
        [("email", ASCENDING)],
        unique=True,
        name="email_1",
    )

    await database.feedback.create_index(
        [("feedback_id", ASCENDING)],
        unique=True,
        name="unique_feedback_id",
    )

    await database.feedback.create_index(
        [("workspace_id", ASCENDING)],
        name="feedback_workspace",
    )

    await database.feedback.create_index(
        [("source", ASCENDING)],
        name="feedback_source",
    )

    await database.feedback.create_index(
        [("ai_analysis.theme", ASCENDING)],
        name="feedback_theme",
    )

    await database.feedback.create_index(
        [
            ("workspace_id", ASCENDING),
            ("ai_analysis.ai_status", ASCENDING),
            ("ai_analysis.analyzed_at", DESCENDING),
        ],
        name="feedback_analysis_status_date",
    )

    await database.feedback.create_index(
        [
            ("workspace_id", ASCENDING),
            ("ai_analysis.feature_category", ASCENDING),
        ],
        name="feedback_feature_category",
    )

    await database.feedback.create_index(
        [
            ("workspace_id", ASCENDING),
            ("ai_analysis.sentiment", ASCENDING),
        ],
        name="feedback_sentiment",
    )

    await database.feedback.create_index(
        [
            ("workspace_id", ASCENDING),
            ("ai_analysis.feature_opportunity_group", ASCENDING),
        ],
        name="feedback_feature_group",
    )

    await database.workspaces.create_index(
        [("owner_id", ASCENDING)],
        name="workspace_owner",
    )

    await database.data_imports.create_index(
        [("workspace_id", ASCENDING)],
        name="data_import_workspace",
    )

    # ---------------------------------------------------------
    # Milestone 3: Features and supporting evidence
    # ---------------------------------------------------------

    await database.features.create_index(
        [("feature_id", ASCENDING)],
        unique=True,
        name="unique_feature_id",
    )

    await database.features.create_index(
        [
            ("workspace_id", ASCENDING),
            ("status", ASCENDING),
            ("updated_at", DESCENDING),
        ],
        name="feature_workspace_status",
    )

    await database.features.create_index(
        [
            ("workspace_id", ASCENDING),
            ("theme", ASCENDING),
        ],
        name="feature_workspace_theme",
    )

    await database.features.create_index(
        [("source_feedback_ids", ASCENDING)],
        name="feature_source_feedback",
    )

    await database.feature_evidence.create_index(
        [("evidence_id", ASCENDING)],
        unique=True,
        name="unique_evidence_id",
    )

    await database.feature_evidence.create_index(
        [
            ("feature_id", ASCENDING),
            ("feedback_id", ASCENDING),
        ],
        unique=True,
        name="unique_feature_feedback_evidence",
    )

    # ---------------------------------------------------------
    # Milestone 3: Priority configuration and scores
    # ---------------------------------------------------------

    await database.priority_configurations.create_index(
        [("configuration_id", ASCENDING)],
        unique=True,
        name="unique_priority_configuration_id",
    )

    await database.priority_configurations.create_index(
        [
            ("workspace_id", ASCENDING),
            ("is_active", ASCENDING),
        ],
        name="priority_configuration_workspace",
    )

    await database.priority_scores.create_index(
        [("priority_score_id", ASCENDING)],
        unique=True,
        name="unique_priority_score_id",
    )

    await database.priority_scores.create_index(
        [
            ("workspace_id", ASCENDING),
            ("feature_id", ASCENDING),
            ("calculated_at", DESCENDING),
        ],
        name="priority_score_feature_history",
    )

    # ---------------------------------------------------------
    # Milestone 3: PRD versions
    # ---------------------------------------------------------

    await database.prds.create_index(
        [
            ("prd_id", ASCENDING),
            ("version", ASCENDING),
        ],
        unique=True,
        name="unique_prd_version",
    )

    await database.prds.create_index(
        [
            ("prd_id", ASCENDING),
            ("is_current", ASCENDING),
        ],
        unique=True,
        partialFilterExpression={"is_current": True},
        name="unique_current_prd",
    )

    await database.prds.create_index(
        [
            ("workspace_id", ASCENDING),
            ("feature_id", ASCENDING),
            ("is_current", ASCENDING),
        ],
        name="prd_feature_current",
    )

    await database.prds.create_index(
        [
            ("workspace_id", ASCENDING),
            ("review_status", ASCENDING),
            ("created_at", DESCENDING),
        ],
        name="prd_review_status",
    )

    # ---------------------------------------------------------
    # Milestone 3: User-story versions
    # ---------------------------------------------------------

    await database.user_stories.create_index(
        [
            ("user_story_id", ASCENDING),
            ("version", ASCENDING),
        ],
        unique=True,
        name="unique_user_story_version",
    )

    await database.user_stories.create_index(
        [
            ("user_story_id", ASCENDING),
            ("is_current", ASCENDING),
        ],
        unique=True,
        partialFilterExpression={"is_current": True},
        name="unique_current_user_story",
    )

    await database.user_stories.create_index(
        [
            ("workspace_id", ASCENDING),
            ("feature_id", ASCENDING),
            ("review_status", ASCENDING),
        ],
        name="user_story_feature_status",
    )

    await database.user_stories.create_index(
        [
            ("prd_id", ASCENDING),
            ("prd_version", ASCENDING),
        ],
        name="user_story_prd",
    )

    # ---------------------------------------------------------
    # Milestone 3: Product Intelligence conversations
    # ---------------------------------------------------------

    await database.conversations.create_index(
        [("conversation_id", ASCENDING)],
        unique=True,
        name="unique_conversation_id",
    )

    await database.conversations.create_index(
        [
            ("workspace_id", ASCENDING),
            ("user_id", ASCENDING),
            ("updated_at", DESCENDING),
        ],
        name="conversation_workspace_user",
    )

    await database.chat_messages.create_index(
        [("message_id", ASCENDING)],
        unique=True,
        name="unique_chat_message_id",
    )

    await database.chat_messages.create_index(
        [
            ("conversation_id", ASCENDING),
            ("created_at", ASCENDING),
        ],
        name="chat_message_conversation_date",
    )

    # ---------------------------------------------------------
    # Milestone 3: Workflow audit history
    # ---------------------------------------------------------

    await database.workflow_events.create_index(
        [("event_id", ASCENDING)],
        unique=True,
        name="unique_workflow_event_id",
    )

    await database.workflow_events.create_index(
        [
            ("workspace_id", ASCENDING),
            ("feature_id", ASCENDING),
            ("created_at", DESCENDING),
        ],
        name="workflow_feature_history",
    )

    # ---------------------------------------------------------
    # Milestone 4: Versioned product roadmaps
    # ---------------------------------------------------------

    await database.roadmaps.create_index(
        [
            ("workspace_id", ASCENDING),
            ("roadmap_id", ASCENDING),
            ("version", ASCENDING),
        ],
        unique=True,
        name="unique_workspace_roadmap_version",
    )

    await database.roadmaps.create_index(
        [
            ("workspace_id", ASCENDING),
            ("roadmap_id", ASCENDING),
            ("is_current", ASCENDING),
        ],
        unique=True,
        partialFilterExpression={"is_current": True},
        name="unique_current_workspace_roadmap",
    )

    await database.roadmaps.create_index(
        [
            ("workspace_id", ASCENDING),
            ("review_status", ASCENDING),
            ("created_at", DESCENDING),
        ],
        name="roadmap_workspace_status_date",
    )

    await database.roadmaps.create_index(
        [
            ("workspace_id", ASCENDING),
            ("milestones.feature_items.feature_id", ASCENDING),
        ],
        name="roadmap_workspace_feature",
    )

    await database.roadmaps.create_index(
        [
            ("workspace_id", ASCENDING),
            ("source_feedback_ids", ASCENDING),
        ],
        name="roadmap_workspace_evidence",
    )

    # ---------------------------------------------------------
    # Milestone 4: Executive-summary versions
    # ---------------------------------------------------------

    await database.executive_summaries.create_index(
        [
            ("workspace_id", ASCENDING),
            ("summary_id", ASCENDING),
            ("version", ASCENDING),
        ],
        unique=True,
        name="unique_workspace_summary_version",
    )

    await database.executive_summaries.create_index(
        [
            ("workspace_id", ASCENDING),
            ("summary_id", ASCENDING),
            ("is_current", ASCENDING),
        ],
        unique=True,
        partialFilterExpression={"is_current": True},
        name="unique_current_workspace_summary",
    )

    await database.executive_summaries.create_index(
        [
            ("workspace_id", ASCENDING),
            ("roadmap_id", ASCENDING),
            ("roadmap_version", DESCENDING),
        ],
        name="summary_workspace_roadmap",
    )

    await database.executive_summaries.create_index(
        [
            ("workspace_id", ASCENDING),
            ("review_status", ASCENDING),
            ("created_at", DESCENDING),
        ],
        name="summary_workspace_status_date",
    )

    # ---------------------------------------------------------
    # Milestone 4: PDF report metadata
    # ---------------------------------------------------------

    await database.report_metadata.create_index(
        [
            ("workspace_id", ASCENDING),
            ("report_id", ASCENDING),
        ],
        unique=True,
        name="unique_workspace_report",
    )

    await database.report_metadata.create_index(
        [
            ("workspace_id", ASCENDING),
            ("generation_status", ASCENDING),
            ("requested_at", DESCENDING),
        ],
        name="report_workspace_status_date",
    )

    await database.report_metadata.create_index(
        [
            ("workspace_id", ASCENDING),
            ("roadmap_id", ASCENDING),
            ("roadmap_version", DESCENDING),
        ],
        name="report_workspace_roadmap",
    )

    # ---------------------------------------------------------
    # Milestone 4: What-if simulations
    # ---------------------------------------------------------

    await database.roadmap_simulations.create_index(
        [
            ("workspace_id", ASCENDING),
            ("simulation_id", ASCENDING),
        ],
        unique=True,
        name="unique_workspace_simulation",
    )

    await database.roadmap_simulations.create_index(
        [
            ("workspace_id", ASCENDING),
            ("roadmap_id", ASCENDING),
            ("created_at", DESCENDING),
        ],
        name="simulation_workspace_roadmap",
    )

    # ---------------------------------------------------------
    # Milestone 4: AI quality and trust evaluations
    # ---------------------------------------------------------

    await database.ai_quality_evaluations.create_index(
        [
            ("workspace_id", ASCENDING),
            ("evaluation_id", ASCENDING),
        ],
        unique=True,
        name="unique_workspace_quality_evaluation",
    )

    await database.ai_quality_evaluations.create_index(
        [
            ("workspace_id", ASCENDING),
            ("entity_type", ASCENDING),
            ("metrics.validation_status", ASCENDING),
            ("created_at", DESCENDING),
        ],
        name="quality_workspace_entity_status",
    )

    await database.ai_quality_evaluations.create_index(
        [
            ("workspace_id", ASCENDING),
            ("entity_id", ASCENDING),
            ("entity_version", DESCENDING),
        ],
        name="quality_workspace_entity_version",
    )