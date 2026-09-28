"""Verify the complete Milestone 3 MongoDB workflow."""

import asyncio
from uuid import uuid4

from database.connection import (
    close_mongodb_connection,
    connect_to_mongodb,
)
from database.conversation_repository import (
    add_chat_message,
    create_conversation,
    get_conversation_with_messages,
)
from database.feature_repository import (
    add_feature_evidence,
    create_feature,
)
from database.priority_repository import (
    create_priority_configuration,
    save_priority_score,
)
from database.requirements_repository import (
    get_current_prd,
    get_prd_history,
    save_prd_version,
    save_user_story_version,
)
from database.traceability_queries import (
    get_feature_traceability,
    record_workflow_event,
)


async def verify_milestone3() -> None:
    """Create, verify and remove temporary Milestone 3 records."""

    token = uuid4().hex

    workspace_id = f"m3-test-workspace-{token}"
    feedback_id = f"m3-test-feedback-{token}"
    feature_id = f"m3-test-feature-{token}"
    evidence_id = f"m3-test-evidence-{token}"
    configuration_id = f"m3-test-config-{token}"
    priority_score_id = f"m3-test-score-{token}"
    prd_id = f"m3-test-prd-{token}"
    user_story_id = f"m3-test-story-{token}"
    criterion_id = f"m3-test-criterion-{token}"
    conversation_id = f"m3-test-conversation-{token}"
    message_id = f"m3-test-message-{token}"
    event_id = f"m3-test-event-{token}"

    database = None

    try:
        database = await connect_to_mongodb()

        # Temporary Milestone 2 feedback evidence.
        await database.feedback.insert_one(
            {
                "feedback_id": feedback_id,
                "workspace_id": workspace_id,
                "source": "milestone3_verification",
                "description": (
                    "The application crashes while processing payments."
                ),
                "ai_analysis": {
                    "ai_status": "completed",
                    "theme": "App Stability",
                    "pain_point": "Payment crashes",
                    "feature_opportunity": (
                        "Improve payment processing stability"
                    ),
                    "feature_category": "Payments",
                },
            }
        )

        # Feature opportunity.
        await create_feature(
            {
                "feature_id": feature_id,
                "workspace_id": workspace_id,
                "title": "Improve payment stability",
                "description": (
                    "Prevent application crashes during payment."
                ),
                "theme": "App Stability",
                "pain_point": "Payment crashes",
                "feature_category": "Payments",
                "source_feedback_ids": [feedback_id],
                "created_by": "milestone3-verification",
            }
        )

        # Feedback-to-feature evidence.
        await add_feature_evidence(
            {
                "evidence_id": evidence_id,
                "workspace_id": workspace_id,
                "feature_id": feature_id,
                "feedback_id": feedback_id,
                "theme": "App Stability",
                "pain_point": "Payment crashes",
                "excerpt": (
                    "The application crashes while processing payments."
                ),
                "relevance_score": 0.95,
            }
        )

        # RICE configuration.
        await create_priority_configuration(
            {
                "configuration_id": configuration_id,
                "workspace_id": workspace_id,
                "name": "Default RICE",
                "method": "RICE",
                "created_by": "milestone3-verification",
            }
        )

        # RICE score: (1000 * 2 * 0.8) / 8 = 200.
        priority = await save_priority_score(
            {
                "priority_score_id": priority_score_id,
                "workspace_id": workspace_id,
                "feature_id": feature_id,
                "configuration_id": configuration_id,
                "method": "RICE",
                "inputs": {
                    "reach": 1000,
                    "impact": 2,
                    "confidence": 80,
                    "effort": 8,
                },
                "recommendation": "High-priority feature",
                "calculated_by": "milestone3-verification",
            }
        )

        assert priority["calculated_score"] == 200.0

        # PRD version 1.
        first_prd = await save_prd_version(
            {
                "prd_id": prd_id,
                "workspace_id": workspace_id,
                "feature_id": feature_id,
                "title": "Payment Stability PRD",
                "content": {
                    "overview": (
                        "Improve reliability of payment processing."
                    ),
                    "problem_statement": (
                        "Customers experience application crashes."
                    ),
                    "target_users": ["Mobile application customers"],
                    "goals": ["Reduce payment crashes"],
                    "functional_requirements": [
                        "Handle payment failures safely"
                    ],
                    "success_metrics": [
                        "Reduce payment crash rate"
                    ],
                },
                "evidence_feedback_ids": [feedback_id],
                "created_by": "milestone3-verification",
            }
        )

        assert first_prd["version"] == 1

        # PRD version 2 proves that editing preserves version history.
        second_prd = await save_prd_version(
            {
                "prd_id": prd_id,
                "workspace_id": workspace_id,
                "feature_id": feature_id,
                "title": "Payment Stability PRD",
                "content": {
                    "overview": (
                        "Improve payment reliability and recovery."
                    ),
                    "problem_statement": (
                        "Customers experience payment crashes."
                    ),
                    "target_users": ["Mobile application customers"],
                    "goals": [
                        "Reduce crashes",
                        "Improve payment recovery",
                    ],
                    "functional_requirements": [
                        "Handle payment failures safely",
                        "Provide retry support",
                    ],
                    "success_metrics": [
                        "Reduce payment crash rate"
                    ],
                },
                "evidence_feedback_ids": [feedback_id],
                "change_summary": "Added payment retry support",
                "generated_by_ai": False,
                "created_by": "milestone3-verification",
            }
        )

        assert second_prd["version"] == 2

        current_prd = await get_current_prd(prd_id)
        prd_history = await get_prd_history(prd_id)

        assert current_prd is not None
        assert current_prd["version"] == 2
        assert len(prd_history) == 2

        # User story and acceptance criteria.
        await save_user_story_version(
            {
                "user_story_id": user_story_id,
                "workspace_id": workspace_id,
                "feature_id": feature_id,
                "prd_id": prd_id,
                "prd_version": 2,
                "title": "Retry failed payment",
                "persona": "mobile application customer",
                "need": "to retry a failed payment safely",
                "value": "I can complete my purchase without restarting",
                "acceptance_criteria": [
                    {
                        "criterion_id": criterion_id,
                        "title": "Safe payment retry",
                        "given": "a payment attempt has failed",
                        "when": "the customer selects retry",
                        "then": (
                            "the application retries without crashing"
                        ),
                    }
                ],
                "evidence_feedback_ids": [feedback_id],
                "priority": "high",
                "created_by": "milestone3-verification",
            }
        )

        # Product Intelligence conversation.
        await create_conversation(
            {
                "conversation_id": conversation_id,
                "workspace_id": workspace_id,
                "user_id": "milestone3-verification",
                "feature_id": feature_id,
                "title": "Payment stability discussion",
            }
        )

        await add_chat_message(
            {
                "message_id": message_id,
                "conversation_id": conversation_id,
                "workspace_id": workspace_id,
                "role": "assistant",
                "content": (
                    "This feature is important because customers "
                    "reported payment crashes."
                ),
                "feature_id": feature_id,
                "prd_id": prd_id,
                "user_story_id": user_story_id,
                "source_feedback_ids": [feedback_id],
            }
        )

        conversation = await get_conversation_with_messages(
            conversation_id
        )

        assert conversation is not None
        assert len(conversation["messages"]) == 1

        # Workflow audit history.
        await record_workflow_event(
            {
                "event_id": event_id,
                "workspace_id": workspace_id,
                "feature_id": feature_id,
                "entity_type": "feature",
                "entity_id": feature_id,
                "action": "requirements_generated",
                "previous_status": "prioritized",
                "new_status": "stories_generated",
                "performed_by": "milestone3-verification",
            }
        )

        # Complete traceability verification.
        traceability = await get_feature_traceability(feature_id)

        assert traceability is not None
        assert len(traceability["feedback"]) == 1
        assert len(traceability["evidence"]) == 1
        assert traceability["priority"] is not None
        assert traceability["prd"] is not None
        assert traceability["prd"]["version"] == 2
        assert len(traceability["user_stories"]) == 1
        assert len(traceability["workflow_history"]) == 1

        print("Milestone 3 database verification successful")
        print("Feature and feedback evidence: successful")
        print("RICE prioritization: successful")
        print("PRD version history: successful")
        print("User stories and acceptance criteria: successful")
        print("Conversation history: successful")
        print("End-to-end traceability: successful")

    finally:
        if database is not None:
            await database.chat_messages.delete_many(
                {"workspace_id": workspace_id}
            )
            await database.conversations.delete_many(
                {"workspace_id": workspace_id}
            )
            await database.workflow_events.delete_many(
                {"workspace_id": workspace_id}
            )
            await database.user_stories.delete_many(
                {"workspace_id": workspace_id}
            )
            await database.prds.delete_many(
                {"workspace_id": workspace_id}
            )
            await database.priority_scores.delete_many(
                {"workspace_id": workspace_id}
            )
            await database.priority_configurations.delete_many(
                {"workspace_id": workspace_id}
            )
            await database.feature_evidence.delete_many(
                {"workspace_id": workspace_id}
            )
            await database.features.delete_many(
                {"workspace_id": workspace_id}
            )
            await database.feedback.delete_many(
                {"feedback_id": feedback_id}
            )

            print("Temporary Milestone 3 test records removed")

        await close_mongodb_connection()


if __name__ == "__main__":
    asyncio.run(verify_milestone3())