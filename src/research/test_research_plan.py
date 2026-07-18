from src.research.research_plan import (
    ResearchPlan,
)
from src.research.research_types import (
    ResearchStatus,
)


def test_research_plan_creates_with_defaults() -> None:
    plan = ResearchPlan(
        title="Market research",
        question_id="question-001",
    )

    assert plan.title == "Market research"
    assert plan.question_id == "question-001"
    assert plan.campaign_ids == []
    assert plan.status == ResearchStatus.NEW


def test_research_plan_adds_campaign_once() -> None:
    plan = ResearchPlan()

    plan.add_campaign(
        "campaign-001",
    )

    plan.add_campaign(
        "campaign-001",
    )

    assert plan.campaign_ids == [
        "campaign-001",
    ]


def test_research_plan_summary_contains_state() -> None:
    plan = ResearchPlan(
        title="Plan",
        question_id="question-001",
    )

    plan.add_campaign(
        "campaign-001",
    )

    summary = plan.summary()

    assert "Research Plan: Plan" in summary
    assert "question-001" in summary
    assert "Campaigns: 1" in summary
    assert "Status: NEW" in summary
