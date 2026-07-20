from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from src.research.engine import ResearchEngine
from src.research.research_campaign import ResearchCampaign


def make_engine() -> ResearchEngine:
    engine = object.__new__(ResearchEngine)
    engine.run = Mock()
    return engine


def make_campaign(
    hypothesis_id: str = "hypothesis-1",
    experiment_ids: list[str] | None = None,
) -> ResearchCampaign:
    return ResearchCampaign(
        hypothesis_id=hypothesis_id,
        experiment_ids=experiment_ids or ["experiment-1"],
    )


def test_run_campaign_calls_callback_for_completed_cycle() -> None:
    engine = make_engine()

    question = SimpleNamespace(id="question-1")
    hypothesis = SimpleNamespace(id="hypothesis-1")
    experiment = SimpleNamespace(id="experiment-1")
    result = SimpleNamespace(id="result-1")

    campaign = make_campaign()
    callback = Mock()

    engine.run.return_value = result

    results = ResearchEngine.run_campaign(
        engine,
        question=question,
        hypothesis=hypothesis,
        campaign=campaign,
        experiments=[experiment],
        executor=Mock(),
        on_cycle_completed=callback,
    )

    assert results == [result]
    callback.assert_called_once_with(
        experiment,
        result,
    )


def test_run_campaign_calls_callback_after_each_cycle() -> None:
    engine = make_engine()

    question = SimpleNamespace(id="question-1")
    hypothesis = SimpleNamespace(id="hypothesis-1")

    first_experiment = SimpleNamespace(id="experiment-1")
    second_experiment = SimpleNamespace(id="experiment-2")

    first_result = SimpleNamespace(id="result-1")
    second_result = SimpleNamespace(id="result-2")

    campaign = make_campaign(
        experiment_ids=[
            first_experiment.id,
            second_experiment.id,
        ]
    )

    callback = Mock()

    engine.run.side_effect = [
        first_result,
        second_result,
    ]

    results = ResearchEngine.run_campaign(
        engine,
        question=question,
        hypothesis=hypothesis,
        campaign=campaign,
        experiments=[
            first_experiment,
            second_experiment,
        ],
        executor=Mock(),
        on_cycle_completed=callback,
    )

    assert results == [
        first_result,
        second_result,
    ]

    assert callback.call_args_list == [
        (
            (
                first_experiment,
                first_result,
            ),
            {},
        ),
        (
            (
                second_experiment,
                second_result,
            ),
            {},
        ),
    ]


def test_run_campaign_does_not_require_callback() -> None:
    engine = make_engine()

    question = SimpleNamespace(id="question-1")
    hypothesis = SimpleNamespace(id="hypothesis-1")
    experiment = SimpleNamespace(id="experiment-1")
    result = SimpleNamespace(id="result-1")

    campaign = make_campaign()

    engine.run.return_value = result

    results = ResearchEngine.run_campaign(
        engine,
        question=question,
        hypothesis=hypothesis,
        campaign=campaign,
        experiments=[experiment],
        executor=Mock(),
    )

    assert results == [result]


def test_run_campaign_preserves_completed_callbacks_before_failure() -> None:
    engine = make_engine()

    question = SimpleNamespace(id="question-1")
    hypothesis = SimpleNamespace(id="hypothesis-1")

    first_experiment = SimpleNamespace(id="experiment-1")
    second_experiment = SimpleNamespace(id="experiment-2")

    first_result = SimpleNamespace(id="result-1")

    campaign = make_campaign(
        experiment_ids=[
            first_experiment.id,
            second_experiment.id,
        ]
    )

    callback = Mock()

    engine.run.side_effect = [
        first_result,
        RuntimeError("cycle failed"),
    ]

    with pytest.raises(
        RuntimeError,
        match="cycle failed",
    ):
        ResearchEngine.run_campaign(
            engine,
            question=question,
            hypothesis=hypothesis,
            campaign=campaign,
            experiments=[
                first_experiment,
                second_experiment,
            ],
            executor=Mock(),
            on_cycle_completed=callback,
        )

    callback.assert_called_once_with(
        first_experiment,
        first_result,
    )