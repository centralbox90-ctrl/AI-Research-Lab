from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from src.research.hypothesis import ResearchHypothesis
from src.research.research_types import HypothesisStatus


def test_research_hypothesis_is_created():
    hypothesis = ResearchHypothesis(
        id="hypothesis-1",
        research_question_id="question-1",
        statement=(
            "Mean return after five bars is positive."
        ),
        expected_direction="positive",
        target_metric="mean_return_5_bars",
        null_condition="mean_return_5_bars <= 0",
        alternative_condition="mean_return_5_bars > 0",
        status=HypothesisStatus.TESTING,
    )

    assert hypothesis.id == "hypothesis-1"
    assert hypothesis.research_question_id == "question-1"
    assert (
        hypothesis.statement
        == "Mean return after five bars is positive."
    )
    assert hypothesis.expected_direction == "positive"
    assert (
        hypothesis.target_metric
        == "mean_return_5_bars"
    )
    assert (
        hypothesis.null_condition
        == "mean_return_5_bars <= 0"
    )
    assert (
        hypothesis.alternative_condition
        == "mean_return_5_bars > 0"
    )
    assert hypothesis.status is HypothesisStatus.TESTING


def test_research_hypothesis_is_immutable():
    hypothesis = ResearchHypothesis(
        research_question_id="question-1",
        statement="Mean return is positive.",
        expected_direction="positive",
        target_metric="mean_return",
        null_condition="mean_return <= 0",
        alternative_condition="mean_return > 0",
    )

    with pytest.raises(FrozenInstanceError):
        hypothesis.statement = "Changed statement"


def test_research_hypothesis_is_serializable():
    hypothesis = ResearchHypothesis(
        id="hypothesis-1",
        research_question_id="question-1",
        statement="Mean return is positive.",
        expected_direction="positive",
        target_metric="mean_return",
        null_condition="mean_return <= 0",
        alternative_condition="mean_return > 0",
        status=HypothesisStatus.NEW,
    )

    assert hypothesis.to_dict() == {
        "id": "hypothesis-1",
        "research_question_id": "question-1",
        "statement": "Mean return is positive.",
        "expected_direction": "positive",
        "target_metric": "mean_return",
        "null_condition": "mean_return <= 0",
        "alternative_condition": "mean_return > 0",
        "status": "NEW",
    }


@pytest.mark.parametrize(
    "field_name",
    [
        "research_question_id",
        "statement",
        "expected_direction",
        "target_metric",
        "null_condition",
        "alternative_condition",
    ],
)
def test_research_hypothesis_rejects_empty_fields(
    field_name,
):
    values = {
        "research_question_id": "question-1",
        "statement": "Mean return is positive.",
        "expected_direction": "positive",
        "target_metric": "mean_return",
        "null_condition": "mean_return <= 0",
        "alternative_condition": "mean_return > 0",
    }
    values[field_name] = "   "

    with pytest.raises(
        ValueError,
        match=f"{field_name} must not be empty",
    ):
        ResearchHypothesis(**values)


def test_research_hypothesis_rejects_invalid_status():
    with pytest.raises(
        TypeError,
        match="status must be a HypothesisStatus",
    ):
        ResearchHypothesis(
            research_question_id="question-1",
            statement="Mean return is positive.",
            expected_direction="positive",
            target_metric="mean_return",
            null_condition="mean_return <= 0",
            alternative_condition="mean_return > 0",
            status="NEW",
        )
