from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from uuid import uuid4

from database.connection import (
    close_mongodb_connection,
    connect_to_mongodb,
    get_database,
)
from database.decision_audit_repository import (
    create_decision_audit,
    get_decision_audit,
    verify_decision_integrity,
)


async def verify_decision_audit() -> None:
    """Verify the tamper-evident decision audit workflow."""

    workspace_id = f"audit-test-workspace-{uuid4()}"
    different_workspace_id = f"other-workspace-{uuid4()}"
    roadmap_id = f"audit-test-roadmap-{uuid4()}"

    database = None

    try:
        await connect_to_mongodb()
        database = get_database()

        approval_time_v1 = datetime.now(timezone.utc).replace(
            microsecond=0
        )

        roadmap_v1 = {
            "roadmap_id": roadmap_id,
            "workspace_id": workspace_id,
            "version": 1,
            "is_current": False,
            "title": "Original Payment Roadmap",
            "description": (
                "Approved roadmap protected by a cryptographic "
                "decision audit."
            ),
            "development_capacity": 50,
            "milestones": [
                {
                    "milestone_id": "milestone-1",
                    "title": "Payment Reliability",
                    "feature_items": [
                        {
                            "feature_id": "feature-payment-retry",
                            "estimated_effort": 20,
                        }
                    ],
                }
            ],
            "source_feedback_ids": [
                "feedback-payment-001",
            ],
            "source_feature_ids": [
                "feature-payment-retry",
            ],
            "roadmap_type": "baseline",
            "review_status": "approved",
            "approved_by": "product-manager-001",
            "approved_at": approval_time_v1,
            "created_at": approval_time_v1,
        }

        await database.roadmaps.insert_one(roadmap_v1)

        audit_v1 = await create_decision_audit(
            workspace_id=workspace_id,
            entity_type="roadmap",
            entity_id=roadmap_id,
            version=1,
        )

        assert audit_v1["algorithm"] == "SHA-256"
        assert len(audit_v1["content_hash"]) == 64
        assert len(audit_v1["chain_hash"]) == 64
        assert audit_v1["previous_hash"] is None

        verification_v1 = await verify_decision_integrity(
            workspace_id=workspace_id,
            entity_type="roadmap",
            entity_id=roadmap_id,
            version=1,
        )

        assert verification_v1["verified"] is True
        assert verification_v1["content_matches"] is True
        assert verification_v1["chain_matches"] is True
        assert (
            verification_v1["previous_link_matches"]
            is True
        )

        # Creating the same audit again must remain idempotent.
        repeated_audit = await create_decision_audit(
            workspace_id=workspace_id,
            entity_type="roadmap",
            entity_id=roadmap_id,
            version=1,
        )

        assert repeated_audit["audit_id"] == audit_v1["audit_id"]

        approval_time_v2 = datetime.now(timezone.utc).replace(
            microsecond=0
        )

        roadmap_v2 = {
            **roadmap_v1,
            "version": 2,
            "is_current": True,
            "title": "Approved Payment Roadmap",
            "description": (
                "Second approved roadmap version with additional "
                "payment recovery planning."
            ),
            "development_capacity": 60,
            "change_summary": (
                "Increased capacity and added recovery planning."
            ),
            "approved_at": approval_time_v2,
            "created_at": approval_time_v2,
        }

        roadmap_v2.pop("_id", None)

        await database.roadmaps.insert_one(roadmap_v2)

        audit_v2 = await create_decision_audit(
            workspace_id=workspace_id,
            entity_type="roadmap",
            entity_id=roadmap_id,
            version=2,
        )

        assert audit_v2["previous_hash"] == audit_v1["chain_hash"]
        assert audit_v2["chain_hash"] != audit_v1["chain_hash"]

        verification_v2 = await verify_decision_integrity(
            workspace_id=workspace_id,
            entity_type="roadmap",
            entity_id=roadmap_id,
            version=2,
        )

        assert verification_v2["verified"] is True

        # Simulate unauthorized modification after approval.
        await database.roadmaps.update_one(
            {
                "workspace_id": workspace_id,
                "roadmap_id": roadmap_id,
                "version": 2,
            },
            {
                "$set": {
                    "title": "Secretly Modified Roadmap",
                }
            },
        )

        tamper_result = await verify_decision_integrity(
            workspace_id=workspace_id,
            entity_type="roadmap",
            entity_id=roadmap_id,
            version=2,
        )

        assert tamper_result["verified"] is False
        assert tamper_result["content_matches"] is False
        assert tamper_result["chain_matches"] is True
        assert tamper_result["previous_link_matches"] is True

        # Restore the original approved content.
        await database.roadmaps.update_one(
            {
                "workspace_id": workspace_id,
                "roadmap_id": roadmap_id,
                "version": 2,
            },
            {
                "$set": {
                    "title": "Approved Payment Roadmap",
                }
            },
        )

        restored_result = await verify_decision_integrity(
            workspace_id=workspace_id,
            entity_type="roadmap",
            entity_id=roadmap_id,
            version=2,
        )

        assert restored_result["verified"] is True

        retrieved_audit = await get_decision_audit(
            workspace_id=workspace_id,
            entity_type="roadmap",
            entity_id=roadmap_id,
            version=2,
        )

        assert retrieved_audit is not None
        assert retrieved_audit["audit_id"] == audit_v2["audit_id"]

        # A different workspace must not access the audit record.
        unauthorized_audit = await get_decision_audit(
            workspace_id=different_workspace_id,
            entity_type="roadmap",
            entity_id=roadmap_id,
            version=2,
        )

        assert unauthorized_audit is None

        unauthorized_verification = (
            await verify_decision_integrity(
                workspace_id=different_workspace_id,
                entity_type="roadmap",
                entity_id=roadmap_id,
                version=2,
            )
        )

        assert unauthorized_verification["verified"] is False

        print("Decision audit verification successful")
        print("Approved roadmap hashing: successful")
        print("SHA-256 hash generation: successful")
        print("Duplicate audit prevention: successful")
        print("Version hash-chain linkage: successful")
        print("Unauthorized tampering detection: successful")
        print("Restored-content verification: successful")
        print("Workspace data isolation: successful")

    finally:
        if database is not None:
            await database.decision_audits.delete_many(
                {
                    "workspace_id": workspace_id,
                }
            )

            await database.roadmaps.delete_many(
                {
                    "workspace_id": workspace_id,
                    "roadmap_id": roadmap_id,
                }
            )

            print("Temporary decision-audit records removed")

        await close_mongodb_connection()


if __name__ == "__main__":
    asyncio.run(verify_decision_audit())