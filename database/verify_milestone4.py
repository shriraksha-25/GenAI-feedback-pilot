"""Verify the complete Milestone 4 database workflow."""

import asyncio
from copy import deepcopy
from uuid import uuid4

from database.connection import (
    close_mongodb_connection,
    connect_to_mongodb,
)
from database.executive_summary_repository import (
    get_current_executive_summary,
    get_executive_summary_history,
    save_executive_summary_version,
)
from database.feature_repository import (
    add_feature_evidence,
    create_feature,
)
from database.priority_repository import (
    save_priority_score,
)
from database.quality_repository import (
    get_quality_dashboard_metrics,
    save_quality_evaluation,
)
from database.report_repository import (
    complete_report,
    create_report_metadata,
    get_report_metadata,
    mark_report_generating,
)
from database.roadmap_queries import (
    get_evidence_linked_roadmap,
    get_product_strategy_context,
    get_roadmap_dashboard_metrics,
)
from database.roadmap_repository import (
    get_current_roadmap,
    get_roadmap_history,
    save_roadmap_version,
)
from database.sample_milestone4_data import (
    build_milestone4_sample_data,
)
from database.simulation_repository import (
    create_roadmap_simulation,
    get_roadmap_simulation,
    save_simulation_result,
)


async def verify_milestone4() -> None:
    """Insert, verify and remove temporary M4 data."""

    token = uuid4().hex
    sample = build_milestone4_sample_data(token)

    workspace_id = sample["workspace_id"]
    roadmap_id = sample["roadmap"]["roadmap_id"]
    summary_id = sample["executive_summary"]["summary_id"]
    report_id = sample["report"]["report_id"]
    simulation_id = sample["simulation"]["simulation_id"]

    database = None

    try:
        database = await connect_to_mongodb()

        # -----------------------------------------------------
        # Feedback, features and evidence
        # -----------------------------------------------------

        await database.feedback.insert_many(
            sample["feedback"]
        )

        for feature in sample["features"]:
            await create_feature(feature)

        for position, feature in enumerate(
            sample["features"]
        ):
            feedback = sample["feedback"][position]

            await add_feature_evidence(
                {
                    "evidence_id": (
                        f"m4-evidence-{position}-{token}"
                    ),
                    "workspace_id": workspace_id,
                    "feature_id": feature["feature_id"],
                    "feedback_id": feedback["feedback_id"],
                    "theme": feature["theme"],
                    "pain_point": feature["pain_point"],
                    "excerpt": feedback["description"],
                    "relevance_score": 0.95,
                }
            )

        # -----------------------------------------------------
        # Feature priority scores
        # -----------------------------------------------------

        saved_scores = []

        for priority_score in sample["priority_scores"]:
            saved_scores.append(
                await save_priority_score(
                    priority_score
                )
            )

        assert saved_scores[0]["calculated_score"] == 225.0
        assert saved_scores[1]["calculated_score"] == 160.0

        # -----------------------------------------------------
        # Roadmap creation and version history
        # -----------------------------------------------------

        roadmap_version_1 = await save_roadmap_version(
            sample["roadmap"]
        )

        assert roadmap_version_1["version"] == 1
        assert roadmap_version_1["is_current"] is True

        revised_roadmap = deepcopy(sample["roadmap"])
        revised_roadmap["development_capacity"] = 65
        revised_roadmap["description"] = (
            "Updated payment roadmap with increased capacity."
        )
        revised_roadmap["change_summary"] = (
            "Development capacity increased from 60 to 65."
        )
        revised_roadmap["generated_by_ai"] = False

        roadmap_version_2 = await save_roadmap_version(
            revised_roadmap
        )

        assert roadmap_version_2["version"] == 2
        assert roadmap_version_2["is_current"] is True

        current_roadmap = await get_current_roadmap(
            workspace_id,
            roadmap_id,
        )
        roadmap_history = await get_roadmap_history(
            workspace_id,
            roadmap_id,
        )

        assert current_roadmap is not None
        assert current_roadmap["version"] == 2
        assert len(roadmap_history) == 2

        # -----------------------------------------------------
        # Executive-summary version history
        # -----------------------------------------------------

        summary_version_1 = (
            await save_executive_summary_version(
                sample["executive_summary"]
            )
        )

        assert summary_version_1["version"] == 1

        revised_summary = deepcopy(
            sample["executive_summary"]
        )
        revised_summary["content"]["overview"] = (
            "Updated strategy covering payment stability, "
            "recovery and increased development capacity."
        )
        revised_summary["change_summary"] = (
            "Added revised capacity information."
        )
        revised_summary["generated_by_ai"] = False

        summary_version_2 = (
            await save_executive_summary_version(
                revised_summary
            )
        )

        assert summary_version_2["version"] == 2

        current_summary = (
            await get_current_executive_summary(
                workspace_id,
                summary_id,
            )
        )
        summary_history = (
            await get_executive_summary_history(
                workspace_id,
                summary_id,
            )
        )

        assert current_summary is not None
        assert current_summary["version"] == 2
        assert len(summary_history) == 2

        # -----------------------------------------------------
        # PDF report metadata lifecycle
        # -----------------------------------------------------

        created_report = await create_report_metadata(
            sample["report"]
        )

        assert (
            created_report["generation_status"]
            == "queued"
        )

        generating_report = await mark_report_generating(
            workspace_id,
            report_id,
        )

        assert generating_report is not None
        assert (
            generating_report["generation_status"]
            == "generating"
        )

        completed_report = await complete_report(
            workspace_id=workspace_id,
            report_id=report_id,
            file_name="payment-strategy-report.pdf",
            storage_key=(
                f"reports/{workspace_id}/"
                "payment-strategy-report.pdf"
            ),
            file_size_bytes=4096,
            content_hash=(
                "sample-sha256-hash-for-verification"
            ),
        )

        assert completed_report is not None
        assert (
            completed_report["generation_status"]
            == "completed"
        )

        retrieved_report = await get_report_metadata(
            workspace_id,
            report_id,
        )

        assert retrieved_report is not None
        assert (
            retrieved_report["mime_type"]
            == "application/pdf"
        )

        # -----------------------------------------------------
        # What-If roadmap simulation
        # -----------------------------------------------------

        created_simulation = (
            await create_roadmap_simulation(
                sample["simulation"]
            )
        )

        assert created_simulation[
            "base_roadmap_version"
        ] == 1

        what_if_roadmap = deepcopy(sample["roadmap"])
        what_if_roadmap["title"] = (
            "Payment Roadmap - Reduced Capacity Scenario"
        )
        what_if_roadmap["development_capacity"] = 45
        what_if_roadmap["roadmap_type"] = "what_if"
        what_if_roadmap["base_roadmap_version"] = 1
        what_if_roadmap["change_summary"] = (
            "Reduced capacity and delayed retry support."
        )

        what_if_version = await save_roadmap_version(
            what_if_roadmap
        )

        assert what_if_version["version"] == 3
        assert what_if_version["is_current"] is False
        assert what_if_version["roadmap_type"] == "what_if"

        simulation_result = await save_simulation_result(
            workspace_id=workspace_id,
            simulation_id=simulation_id,
            result_roadmap_version=3,
            comparison=sample["simulation"]["comparison"],
        )

        assert simulation_result is not None
        assert simulation_result[
            "result_roadmap_version"
        ] == 3

        retrieved_simulation = (
            await get_roadmap_simulation(
                workspace_id,
                simulation_id,
            )
        )

        assert retrieved_simulation is not None

        # A what-if scenario must not replace the baseline.
        current_after_simulation = (
            await get_current_roadmap(
                workspace_id,
                roadmap_id,
            )
        )

        assert current_after_simulation is not None
        assert current_after_simulation["version"] == 2
        assert (
            current_after_simulation["roadmap_type"]
            == "baseline"
        )

        # -----------------------------------------------------
        # AI Quality & Trust Dashboard data
        # -----------------------------------------------------

        saved_evaluation = await save_quality_evaluation(
            sample["quality_evaluation"]
        )

        assert (
            saved_evaluation["metrics"][
                "validation_status"
            ]
            == "passed"
        )

        quality_metrics = (
            await get_quality_dashboard_metrics(
                workspace_id
            )
        )

        assert quality_metrics[
            "evaluation_count"
        ] == 1
        assert quality_metrics[
            "average_evidence_coverage"
        ] == 1.0

        # -----------------------------------------------------
        # Evidence-linked roadmap and dashboard queries
        # -----------------------------------------------------

        evidence_roadmap = (
            await get_evidence_linked_roadmap(
                workspace_id,
                roadmap_id,
            )
        )

        assert evidence_roadmap is not None
        assert evidence_roadmap["version"] == 2

        enriched_items = []

        for milestone in evidence_roadmap["milestones"]:
            enriched_items.extend(
                milestone["feature_items"]
            )

        assert len(enriched_items) == 2
        assert all(
            item["feature"] is not None
            for item in enriched_items
        )
        assert all(
            item["latest_priority"] is not None
            for item in enriched_items
        )
        assert all(
            len(item["supporting_feedback"]) >= 1
            for item in enriched_items
        )

        dashboard_metrics = (
            await get_roadmap_dashboard_metrics(
                workspace_id,
                roadmap_id,
            )
        )

        assert dashboard_metrics is not None
        assert dashboard_metrics["feature_count"] == 2
        assert (
            dashboard_metrics[
                "total_estimated_effort"
            ]
            == 50.0
        )

        strategy_context = (
            await get_product_strategy_context(
                workspace_id,
                roadmap_id,
            )
        )

        assert strategy_context is not None
        assert (
            strategy_context["executive_summary"]
            is not None
        )

        # -----------------------------------------------------
        # Workspace isolation
        # -----------------------------------------------------

        unauthorized_roadmap = await get_current_roadmap(
            "different-workspace",
            roadmap_id,
        )

        unauthorized_report = await get_report_metadata(
            "different-workspace",
            report_id,
        )

        assert unauthorized_roadmap is None
        assert unauthorized_report is None

        print("Milestone 4 database verification successful")
        print("Roadmap creation and retrieval: successful")
        print("Roadmap version history: successful")
        print("Milestone and dependency integrity: successful")
        print("Executive-summary versions: successful")
        print("PDF report metadata lifecycle: successful")
        print("Evidence-linked roadmap: successful")
        print("Roadmap dashboard metrics: successful")
        print("What-if simulation: successful")
        print("AI quality and trust metrics: successful")
        print("Workspace data isolation: successful")

    finally:
        if database is not None:
            await database.ai_quality_evaluations.delete_many(
                {"workspace_id": workspace_id}
            )
            await database.roadmap_simulations.delete_many(
                {"workspace_id": workspace_id}
            )
            await database.report_metadata.delete_many(
                {"workspace_id": workspace_id}
            )
            await database.executive_summaries.delete_many(
                {"workspace_id": workspace_id}
            )
            await database.roadmaps.delete_many(
                {"workspace_id": workspace_id}
            )
            await database.feature_evidence.delete_many(
                {"workspace_id": workspace_id}
            )
            await database.priority_scores.delete_many(
                {"workspace_id": workspace_id}
            )
            await database.features.delete_many(
                {"workspace_id": workspace_id}
            )
            await database.feedback.delete_many(
                {"workspace_id": workspace_id}
            )

            print(
                "Temporary Milestone 4 test records removed"
            )

        await close_mongodb_connection()


if __name__ == "__main__":
    asyncio.run(verify_milestone4())
