import pytest

from src.application.prepared_market_campaign_executor import (
    PreparedMarketCampaignExecutor,
)
from src.research import (
    Experiment,
    ExperimentResult,
)


class RecordingExecutor:
    """
    Records the experiment passed to the executor.
    """

    def __init__(self) -> None:
        self.received_experiment: Experiment | None = None

    def __call__(
        self,
        experiment: Experiment,
    ) -> ExperimentResult:
        self.received_experiment = experiment

        return ExperimentResult(
            experiment_id=experiment.id,
            success=True,
            metrics={},
            observations={},
            conclusion="Experiment completed.",
        )


def build_experiment(
    title: str,
) -> Experiment:
    return Experiment(
        hypothesis_id="hypothesis:001",
        title=title,
        description=f"Description for {title}.",
        parameters={},
    )


def test_prepared_market_campaign_executor_routes_experiment() -> None:
    experiment_a = build_experiment(
        "Experiment A"
    )
    experiment_b = build_experiment(
        "Experiment B"
    )

    executor_a = RecordingExecutor()
    executor_b = RecordingExecutor()

    campaign_executor = PreparedMarketCampaignExecutor(
        {
            experiment_a.id: executor_a,
            experiment_b.id: executor_b,
        }
    )

    result = campaign_executor(
        experiment_a
    )

    assert executor_a.received_experiment is experiment_a
    assert executor_b.received_experiment is None
    assert result.experiment_id == experiment_a.id


def test_prepared_market_campaign_executor_routes_second_experiment() -> None:
    experiment_a = build_experiment(
        "Experiment A"
    )
    experiment_b = build_experiment(
        "Experiment B"
    )

    executor_a = RecordingExecutor()
    executor_b = RecordingExecutor()

    campaign_executor = PreparedMarketCampaignExecutor(
        {
            experiment_a.id: executor_a,
            experiment_b.id: executor_b,
        }
    )

    result = campaign_executor(
        experiment_b
    )

    assert executor_a.received_experiment is None
    assert executor_b.received_experiment is experiment_b
    assert result.experiment_id == experiment_b.id


def test_prepared_market_campaign_executor_rejects_unknown_experiment() -> None:
    known_experiment = build_experiment(
        "Known experiment"
    )
    unknown_experiment = build_experiment(
        "Unknown experiment"
    )

    campaign_executor = PreparedMarketCampaignExecutor(
        {
            known_experiment.id: RecordingExecutor(),
        }
    )

    with pytest.raises(
        ValueError,
        match="no prepared executor for experiment",
    ):
        campaign_executor(
            unknown_experiment
        )
