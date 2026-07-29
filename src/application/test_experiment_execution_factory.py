from datetime import UTC, datetime

import pytest

from src.application.experiment_execution_factory import (
    ExperimentExecutionFactory,
)
from src.application.market_experiment_specification import (
    MarketExperimentSpecification,
    MarketPositionDirection,
)
from src.research.experiment_execution import (
    ExperimentExecutionStatus,
)


CREATED_AT = datetime(
    2026,
    7,
    28,
    12,
    30,
    tzinfo=UTC,
)


class StubClock:

    def __init__(
        self,
        current_time: datetime,
    ) -> None:
        self.current_time = current_time
        self.call_count = 0

    def now(self) -> datetime:
        self.call_count += 1

        return self.current_time


class StubIdGenerator:

    def __init__(
        self,
        generated_id: str,
    ) -> None:
        self.generated_id = generated_id
        self.call_count = 0

    def generate(self) -> str:
        self.call_count += 1

        return self.generated_id


def build_specification() -> MarketExperimentSpecification:
    return MarketExperimentSpecification(
        executor_type="market_backtest",
        question_title="Does the condition predict returns?",
        question_description=(
            "Test the condition on historical market data."
        ),
        hypothesis_title="The condition predicts returns",
        hypothesis_description=(
            "Expected returns differ after the condition."
        ),
        expected_result="A measurable return difference.",
        experiment_title="Historical market experiment",
        experiment_description=(
            "Execute the registered rules on canonical data."
        ),
        data_source="historical_csv",
        symbol="BTCUSDT",
        timeframe="1h",
        start_at=datetime(
            2024,
            1,
            1,
            tzinfo=UTC,
        ),
        end_at=datetime(
            2024,
            12,
            31,
            tzinfo=UTC,
        ),
        entry_rule="registered_entry",
        exit_rule="registered_exit",
        direction=MarketPositionDirection.LONG,
        stop_loss_percent=1.0,
        take_profit_percent=2.0,
        max_holding_bars=24,
        commission_percent=0.1,
        slippage_percent=0.05,
        strategy_parameters={
            "period": 14,
        },
        tags=(
            "btc",
            "historical",
        ),
    )


def test_creates_pending_execution() -> None:
    clock = StubClock(CREATED_AT)
    id_generator = StubIdGenerator(
        "execution-id"
    )
    specification = build_specification()
    factory = ExperimentExecutionFactory(
        clock=clock,
        id_generator=id_generator,
    )

    execution = factory.create_pending(
        specification=specification,
        experiment_id=" experiment-id ",
        correlation_id=" correlation-id ",
    )

    assert execution.execution_id == "execution-id"
    assert execution.experiment_id == "experiment-id"
    assert execution.specification_fingerprint == (
        specification.fingerprint
    )
    assert execution.correlation_id == "correlation-id"
    assert execution.created_at == CREATED_AT
    assert execution.status is (
        ExperimentExecutionStatus.PENDING
    )
    assert execution.environment_fingerprint is None
    assert execution.started_at is None
    assert execution.finished_at is None
    assert execution.result_id is None
    assert execution.failure is None
    assert clock.call_count == 1
    assert id_generator.call_count == 1


def test_correlation_id_is_optional() -> None:
    factory = ExperimentExecutionFactory(
        clock=StubClock(CREATED_AT),
        id_generator=StubIdGenerator(
            "execution-id"
        ),
    )

    execution = factory.create_pending(
        specification=build_specification(),
        experiment_id="experiment-id",
    )

    assert execution.correlation_id is None


def test_rejects_invalid_specification_before_using_ports(
) -> None:
    clock = StubClock(CREATED_AT)
    id_generator = StubIdGenerator(
        "execution-id"
    )
    factory = ExperimentExecutionFactory(
        clock=clock,
        id_generator=id_generator,
    )

    with pytest.raises(
        TypeError,
        match=(
            "specification must be a "
            "MarketExperimentSpecification"
        ),
    ):
        factory.create_pending(
            specification=object(),
            experiment_id="experiment-id",
        )

    assert clock.call_count == 0
    assert id_generator.call_count == 0


def test_delegates_identity_validation_to_execution(
) -> None:
    factory = ExperimentExecutionFactory(
        clock=StubClock(CREATED_AT),
        id_generator=StubIdGenerator(
            "execution-id"
        ),
    )

    with pytest.raises(
        ValueError,
        match="experiment_id must not be empty",
    ):
        factory.create_pending(
            specification=build_specification(),
            experiment_id="   ",
        )


def test_delegates_clock_validation_to_execution(
) -> None:
    factory = ExperimentExecutionFactory(
        clock=StubClock(
            datetime(2026, 7, 28, 12, 30)
        ),
        id_generator=StubIdGenerator(
            "execution-id"
        ),
    )

    with pytest.raises(
        ValueError,
        match="created_at must be timezone-aware",
    ):
        factory.create_pending(
            specification=build_specification(),
            experiment_id="experiment-id",
        )


def test_creates_pending_execution_from_fingerprint(
) -> None:
    clock = StubClock(CREATED_AT)
    id_generator = StubIdGenerator(
        "comparative-execution-id"
    )
    factory = ExperimentExecutionFactory(
        clock=clock,
        id_generator=id_generator,
    )

    execution = (
        factory.create_pending_from_fingerprint(
            specification_fingerprint="c" * 64,
            experiment_id=(
                "comparative-experiment-id"
            ),
            correlation_id=(
                "comparative-correlation-id"
            ),
        )
    )

    assert execution.execution_id == (
        "comparative-execution-id"
    )
    assert execution.experiment_id == (
        "comparative-experiment-id"
    )
    assert execution.specification_fingerprint == (
        "c" * 64
    )
    assert execution.correlation_id == (
        "comparative-correlation-id"
    )
    assert execution.created_at == CREATED_AT
    assert execution.status is (
        ExperimentExecutionStatus.PENDING
    )
    assert clock.call_count == 1
    assert id_generator.call_count == 1


def test_fingerprint_creation_delegates_validation_to_execution(
) -> None:
    factory = ExperimentExecutionFactory(
        clock=StubClock(CREATED_AT),
        id_generator=StubIdGenerator(
            "execution-id"
        ),
    )

    with pytest.raises(
        ValueError,
        match=(
            "specification_fingerprint must be "
            "a lowercase SHA-256 hexadecimal string"
        ),
    ):
        factory.create_pending_from_fingerprint(
            specification_fingerprint=(
                "invalid-fingerprint"
            ),
            experiment_id="experiment-id",
        )