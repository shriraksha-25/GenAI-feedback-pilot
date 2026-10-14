"""Realistic Milestone 4 sample data for integration testing."""

from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4


def build_milestone4_sample_data(
    token: str | None = None,
) -> dict[str, Any]:
    """Build an isolated product-roadmap test dataset."""

    unique_token = token or uuid4().hex

    workspace_id = f"m4-workspace-{unique_token}"

    feedback_1_id = f"m4-feedback-payment-{unique_token}"
    feedback_2_id = f"m4-feedback-retry-{unique_token}"

    feature_1_id = f"m4-feature-stability-{unique_token}"
    feature_2_id = f"m4-feature-retry-{unique_token}"

    score_1_id = f"m4-score-stability-{unique_token}"
    score_2_id = f"m4-score-retry-{unique_token}"

    roadmap_id = f"m4-roadmap-{unique_token}"
    summary_id = f"m4-summary-{unique_token}"
    report_id = f"m4-report-{unique_token}"
    simulation_id = f"m4-simulation-{unique_token}"
    evaluation_id = f"m4-evaluation-{unique_token}"

    start_date = datetime.now(timezone.utc)
    milestone_1_end = start_date + timedelta(days=30)
    milestone_2_end = start_date + timedelta(days=60)

    feedback = [
        {
            "feedback_id": feedback_1_id,
            "workspace_id": workspace_id,
            "source": "customer_support",
            "product": "Mobile Application",
            "description": (
                "The mobile application crashes during payment."
            ),
            "priority": "high",
            "ai_analysis": {
                "ai_status": "completed",
                "theme": "Payment Reliability",
                "sentiment": "negative",
                "pain_point": "Payment crashes",
                "feature_opportunity": (
                    "Improve payment processing stability"
                ),
                "feature_category": "Payments",
            },
        },
        {
            "feedback_id": feedback_2_id,
            "workspace_id": workspace_id,
            "source": "app_review",
            "product": "Mobile Application",
            "description": (
                "Customers cannot safely retry a failed payment."
            ),
            "priority": "high",
            "ai_analysis": {
                "ai_status": "completed",
                "theme": "Payment Recovery",
                "sentiment": "negative",
                "pain_point": "No safe retry option",
                "feature_opportunity": (
                    "Add safe payment retry support"
                ),
                "feature_category": "Payments",
            },
        },
    ]

    features = [
        {
            "feature_id": feature_1_id,
            "workspace_id": workspace_id,
            "title": "Improve payment stability",
            "description": (
                "Prevent crashes during payment processing."
            ),
            "theme": "Payment Reliability",
            "pain_point": "Payment crashes",
            "feature_category": "Payments",
            "source_feedback_ids": [feedback_1_id],
            "created_by": "milestone4-sample",
        },
        {
            "feature_id": feature_2_id,
            "workspace_id": workspace_id,
            "title": "Add safe payment retry",
            "description": (
                "Allow customers to retry failed payments."
            ),
            "theme": "Payment Recovery",
            "pain_point": "No safe retry option",
            "feature_category": "Payments",
            "source_feedback_ids": [feedback_2_id],
            "created_by": "milestone4-sample",
        },
    ]

    priority_scores = [
        {
            "priority_score_id": score_1_id,
            "workspace_id": workspace_id,
            "feature_id": feature_1_id,
            "method": "RICE",
            "inputs": {
                "reach": 1000,
                "impact": 3,
                "confidence": 90,
                "effort": 12,
            },
            "recommendation": (
                "Schedule first because payment crashes "
                "block customer purchases."
            ),
            "calculated_by": "milestone4-sample",
        },
        {
            "priority_score_id": score_2_id,
            "workspace_id": workspace_id,
            "feature_id": feature_2_id,
            "method": "RICE",
            "inputs": {
                "reach": 800,
                "impact": 2,
                "confidence": 80,
                "effort": 8,
            },
            "recommendation": (
                "Schedule after stability improvements."
            ),
            "calculated_by": "milestone4-sample",
        },
    ]

    roadmap = {
        "roadmap_id": roadmap_id,
        "workspace_id": workspace_id,
        "title": "Payment Experience Roadmap",
        "description": (
            "A roadmap for payment stability and recovery."
        ),
        "planning_horizon_start": start_date,
        "planning_horizon_end": milestone_2_end,
        "development_capacity": 60,
        "capacity_unit": "story_points",
        "planning_assumptions": [
            {
                "assumption_id": (
                    f"m4-assumption-{unique_token}"
                ),
                "category": "team_capacity",
                "description": (
                    "The payment team has 60 story points."
                ),
                "value": 60,
                "source": "product_manager",
            }
        ],
        "milestones": [
            {
                "milestone_id": (
                    f"m4-milestone-stability-{unique_token}"
                ),
                "name": "Payment Stability",
                "description": (
                    "Stabilize the payment processing flow."
                ),
                "sequence": 1,
                "start_date": start_date,
                "end_date": milestone_1_end,
                "feature_items": [
                    {
                        "feature_id": feature_1_id,
                        "priority_score_id": score_1_id,
                        "priority_score": 225.0,
                        "estimated_effort": 30,
                        "estimated_impact": 9,
                        "sequence_order": 1,
                        "planned_start": start_date,
                        "planned_end": milestone_1_end,
                        "source_feedback_ids": [
                            feedback_1_id
                        ],
                        "pain_points": [
                            "Payment crashes"
                        ],
                        "scheduling_reason": (
                            "Highest customer and revenue impact."
                        ),
                        "risk_level": "critical",
                    }
                ],
            },
            {
                "milestone_id": (
                    f"m4-milestone-retry-{unique_token}"
                ),
                "name": "Payment Recovery",
                "description": (
                    "Add safe recovery for failed payments."
                ),
                "sequence": 2,
                "start_date": milestone_1_end,
                "end_date": milestone_2_end,
                "feature_items": [
                    {
                        "feature_id": feature_2_id,
                        "priority_score_id": score_2_id,
                        "priority_score": 160.0,
                        "estimated_effort": 20,
                        "estimated_impact": 7,
                        "sequence_order": 1,
                        "planned_start": milestone_1_end,
                        "planned_end": milestone_2_end,
                        "source_feedback_ids": [
                            feedback_2_id
                        ],
                        "pain_points": [
                            "No safe retry option"
                        ],
                        "scheduling_reason": (
                            "Depends on a stable payment flow."
                        ),
                        "dependency_feature_ids": [
                            feature_1_id
                        ],
                        "risk_level": "high",
                    }
                ],
            },
        ],
        "dependencies": [
            {
                "dependency_id": (
                    f"m4-dependency-{unique_token}"
                ),
                "feature_id": feature_2_id,
                "depends_on_feature_id": feature_1_id,
                "description": (
                    "Retry support requires stable payments."
                ),
            }
        ],
        "source_feedback_ids": [
            feedback_1_id,
            feedback_2_id,
        ],
        "source_feature_ids": [
            feature_1_id,
            feature_2_id,
        ],
        "quality_metrics": {
            "validation_status": "passed",
            "completeness_score": 0.95,
            "relevance_score": 0.96,
            "evidence_coverage": 1.0,
            "response_time_ms": 850,
            "model_name": "sample-roadmap-agent",
            "evaluated_at": start_date,
        },
        "created_by": "milestone4-sample",
    }

    executive_summary = {
        "summary_id": summary_id,
        "workspace_id": workspace_id,
        "roadmap_id": roadmap_id,
        "roadmap_version": 1,
        "title": "Payment Strategy Executive Summary",
        "content": {
            "overview": (
                "Customers report payment crashes and "
                "limited failure recovery."
            ),
            "customer_pain_points": [
                "Payment crashes",
                "No safe retry option",
            ],
            "priority_features": [
                "Improve payment stability",
                "Add safe payment retry",
            ],
            "product_opportunities": [
                "Increase successful payment completion"
            ],
            "roadmap_highlights": [
                "Stability is completed before retry support"
            ],
            "risks": [
                "Payment-provider integration complexity"
            ],
            "dependencies": [
                "Retry support depends on payment stability"
            ],
            "recommendations": [
                "Build payment stability first"
            ],
            "expected_outcomes": [
                "Reduced payment failure rate",
                "Improved customer satisfaction",
            ],
        },
        "source_feedback_ids": [
            feedback_1_id,
            feedback_2_id,
        ],
        "source_feature_ids": [
            feature_1_id,
            feature_2_id,
        ],
        "quality_metrics": {
            "validation_status": "passed",
            "completeness_score": 0.94,
            "relevance_score": 0.95,
            "evidence_coverage": 1.0,
            "response_time_ms": 600,
            "model_name": "sample-summary-agent",
            "evaluated_at": start_date,
        },
        "created_by": "milestone4-sample",
    }

    report = {
        "report_id": report_id,
        "workspace_id": workspace_id,
        "report_type": "executive_summary",
        "roadmap_id": roadmap_id,
        "roadmap_version": 1,
        "summary_id": summary_id,
        "summary_version": 1,
        "generated_by": "milestone4-sample",
    }

    simulation = {
        "simulation_id": simulation_id,
        "workspace_id": workspace_id,
        "roadmap_id": roadmap_id,
        "base_roadmap_version": 1,
        "name": "Reduced capacity scenario",
        "description": (
            "Compare the roadmap after reducing capacity."
        ),
        "modified_capacity": 45,
        "delayed_feature_ids": [feature_2_id],
        "comparison": {
            "original_capacity": 60,
            "revised_capacity": 45,
            "original_feature_count": 2,
            "revised_feature_count": 2,
            "original_total_effort": 50,
            "revised_total_effort": 50,
            "original_expected_impact": 16,
            "revised_expected_impact": 16,
        },
        "created_by": "milestone4-sample",
    }

    quality_evaluation = {
        "evaluation_id": evaluation_id,
        "workspace_id": workspace_id,
        "entity_type": "roadmap",
        "entity_id": roadmap_id,
        "entity_version": 1,
        "metrics": {
            "validation_status": "passed",
            "completeness_score": 0.95,
            "relevance_score": 0.96,
            "evidence_coverage": 1.0,
            "response_time_ms": 850,
            "model_name": "sample-roadmap-agent",
            "evaluated_at": start_date,
        },
    }

    return {
        "workspace_id": workspace_id,
        "feedback": feedback,
        "features": features,
        "priority_scores": priority_scores,
        "roadmap": roadmap,
        "executive_summary": executive_summary,
        "report": report,
        "simulation": simulation,
        "quality_evaluation": quality_evaluation,
    }