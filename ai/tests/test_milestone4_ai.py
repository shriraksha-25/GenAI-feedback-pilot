
import asyncio
from datetime import datetime, timezone

import pytest

from ai.services.roadmap_planner import (
    generate_roadmap,
    simulate_roadmap,
    explain_priority_recommendation,
)
from ai.services.executive_summary_generator import generate_executive_summary


@pytest.fixture(autouse=True)
def disable_external_llm(monkeypatch):
    """Keep roadmap unit tests deterministic and independent of API access."""
    from ai.agents import llm

    def no_llm():
        raise RuntimeError("LLM disabled in unit tests")

    monkeypatch.setattr(llm, "get_llm", no_llm)


def test_roadmap_preserves_evidence_and_orders_dependencies():
    roadmap = asyncio.run(generate_roadmap(
        [
            {
                "feature_id": "f2",
                "title": "Retry payment",
                "effort": 5,
                "priority_score": 99,
                "dependencies": ["f1"],
                "source_feedback_ids": ["fb2"],
            },
            {
                "feature_id": "f1",
                "title": "Payment stability",
                "effort": 5,
                "priority_score": 10,
                "source_feedback_ids": ["fb1"],
            },
        ],
        feedback=[{"feedback_id": "fb1"}, {"feedback_id": "fb2"}],
        workspace_id="w1",
        roadmap_id="r1",
        horizon_start=datetime(2026, 1, 1, tzinfo=timezone.utc),
        capacity_per_milestone=10,
    ))

    assert roadmap["source_feedback_ids"] == ["fb1", "fb2"]
    assert roadmap["milestones"][0]["feature_items"][0]["feature_id"] == "f1"
    assert roadmap["milestones"][1]["feature_items"][0]["feature_id"] == "f2"
    assert roadmap["dependencies"][0]["depends_on_feature_id"] == "f1"
    assert roadmap["generated_by_ai"] is False


def test_roadmap_warns_when_effort_missing():
    result = asyncio.run(
        generate_roadmap([{"feature_id": "f1", "title": "Missing effort"}])
    )

    assert result["milestones"] == []
    assert any(
        "estimated effort" in warning
        for warning in result["quality_metrics"]["warnings"]
    )


def test_roadmap_rejects_duplicate_ids_and_dependency_cycles():
    with pytest.raises(ValueError, match="Duplicate feature ID"):
        asyncio.run(generate_roadmap([
            {"feature_id": "f1"},
            {"feature_id": "f1"},
        ]))

    with pytest.raises(ValueError, match="Dependency cycle"):
        asyncio.run(generate_roadmap([
            {"feature_id": "f1", "effort": 1, "dependencies": ["f2"]},
            {"feature_id": "f2", "effort": 1, "dependencies": ["f1"]},
        ]))


def test_simulation_does_not_mutate_original():
    roadmap = asyncio.run(generate_roadmap([
        {"feature_id": "f1", "effort": 2, "source_feedback_ids": ["fb1"]},
        {"feature_id": "f2", "effort": 2},
    ], capacity_per_milestone=10))

    original_count = sum(
        len(m["feature_items"]) for m in roadmap["milestones"]
    )

    result = simulate_roadmap(
        roadmap,
        modified_capacity=5,
        delayed_feature_ids=["f2"],
    )

    assert result["roadmap"]["roadmap_type"] == "what_if"
    assert sum(
        len(m["feature_items"]) for m in roadmap["milestones"]
    ) == original_count
    assert result["comparison"]["delayed_feature_ids"] == ["f2"]


def test_summary_rejects_empty_roadmap():
    result = asyncio.run(generate_executive_summary({}))

    assert result["status"] == "failed"
    assert result["summary"] is None


def test_what_if_repacks_under_reduced_capacity_and_reports_moves():
    roadmap = asyncio.run(generate_roadmap([
        {"feature_id": "f1", "effort": 6, "priority_score": 10},
        {"feature_id": "f2", "effort": 4, "priority_score": 9},
    ], capacity_per_milestone=10, max_milestones=3))

    result = simulate_roadmap(roadmap, modified_capacity=6)

    assert result["comparison"]["revised_capacity"] == 6
    assert result["comparison"]["revised_feature_count"] == 2
    assert len(result["roadmap"]["milestones"]) >= 2
    assert result["comparison"]["moved_feature_ids"]


def test_priority_explanation_reuses_score_and_flags_missing_factors():
    result = explain_priority_recommendation({
        "feature_id": "f1",
        "priority_score": 42,
        "priority_factors": {"reach": 100, "impact": 2, "effort": 5},
        "source_feedback_ids": ["fb1"],
    })

    assert result["priority_score"] == 42
    assert result["supporting_feedback_ids"] == ["fb1"]
    assert result["explanation_complete"] is True

    missing = explain_priority_recommendation({"feature_id": "f2"})

    assert missing["explanation_complete"] is False
    assert "priority_score" in missing["missing_information"]


def test_unknown_simulation_feature_is_rejected():
    roadmap = asyncio.run(
        generate_roadmap([{"feature_id": "f1", "effort": 1}])
    )

    with pytest.raises(ValueError, match="Unknown feature IDs"):
        simulate_roadmap(roadmap, delayed_feature_ids=["not-real"])
