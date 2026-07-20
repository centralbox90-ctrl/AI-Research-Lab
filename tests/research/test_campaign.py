from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import datetime, timezone

import pytest

from src.research.assumption import AssumptionSet
from src.research.campaign import Campaign
from src.research.hypothesis import ResearchHypothesis
from src.research.question import ResearchQuestion
from src.research.research_types import ResearchStatus


class SpecificationStub:
    def __init__(self, fingerprint: str) -> None:
        self.fingerprint = fingerprint


def build_campaign(
    *,
    campaign_id: str = "campaign-1",
    status: ResearchStatus = ResearchStatus.NEW,
) -> Campaign:
    question = ResearchQuestion(
        id="question-1",
        statement="How does the market respond?",
    )

    hypothesis = ResearchHypothesis(
        id="hypothesis-1",
        research_question_id=question.id,
        statement="Mean return is positive.",
        expected_direction="positive",
        target_metric="mean_return",
        null_condition="mean_return <= 0",
        alternative_condition="mean_return > 0",
    )

    assumption_set = AssumptionSet(
        id="assumption-set-1",
        assumptions=(),
    )

    specification = SpecificationStub(
        fingerprint="specification-fingerprint-1",
    )

    return Campaign(
        id=campaign_id,
        research_question=question,
        hypothesis=hypothesis,
        assumption_set=assumption_set,
        specifications=(specification,),
        created_at=datetime(
            2026,
            7,
            19,
            12,
            0,
            tzinfo=timezone.utc,
        ),
        status=status,
    )


def test_campaign_is_created() -> None:
    campaign = build_campaign()

    assert campaign.id == "campaign-1"
    assert campaign.research_question.id == "question-1"
    assert campaign.hypothesis.id == "hypothesis-1"
    assert campaign.assumption_set.id == "assumption-set-1"
    assert len(campaign.specifications) == 1
    assert campaign.status is ResearchStatus.NEW


def test_campaign_is_immutable() -> None:
    campaign = build_campaign()

    with pytest.raises(FrozenInstanceError):
        campaign.status = ResearchStatus.RUNNING


def test_campaign_is_serializable() -> None:
    campaign = build_campaign()

    assert campaign.to_dict() == {
        "id": "campaign-1",
        "research_question_id": "question-1",
        "hypothesis_id": "hypothesis-1",
        "assumption_set_id": "assumption-set-1",
        "specification_fingerprints": [
            "specification-fingerprint-1",
        ],
        "created_at": "2026-07-19T12:00:00+00:00",
        "status": "NEW",
    }


def test_campaign_rejects_empty_id() -> None:
    with pytest.raises(
        ValueError,
        match="id must not be empty",
    ):
        build_campaign(campaign_id="   ")


def test_campaign_rejects_empty_specifications() -> None:
    campaign = build_campaign()

    with pytest.raises(
        ValueError,
        match="specifications must not be empty",
    ):
        Campaign(
            research_question=campaign.research_question,
            hypothesis=campaign.hypothesis,
            assumption_set=campaign.assumption_set,
            specifications=(),
        )


def test_campaign_rejects_invalid_status() -> None:
    with pytest.raises(
        TypeError,
        match="status must be a ResearchStatus",
    ):
        build_campaign(status="NEW")
