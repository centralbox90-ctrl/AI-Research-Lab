import pytest

from src.application.research_runtime_configuration import (
    ResearchRuntimeConfiguration,
)


def test_runtime_configuration_accepts_valid_values() -> None:
    configuration = ResearchRuntimeConfiguration(
        code_version="git:abc123",
        executor_version="backtest-engine:v1",
        statistical_method_version="statistics:v1",
        random_seed=42,
    )

    assert configuration.code_version == "git:abc123"
    assert configuration.executor_version == "backtest-engine:v1"
    assert (
        configuration.statistical_method_version
        == "statistics:v1"
    )
    assert configuration.random_seed == 42


@pytest.mark.parametrize(
    "field_name",
    [
        "code_version",
        "executor_version",
        "statistical_method_version",
    ],
)
def test_runtime_configuration_rejects_empty_version(
    field_name: str,
) -> None:
    values = {
        "code_version": "git:abc123",
        "executor_version": "backtest-engine:v1",
        "statistical_method_version": "statistics:v1",
        "random_seed": 42,
    }

    values[field_name] = ""

    with pytest.raises(
        ValueError,
        match=field_name,
    ):
        ResearchRuntimeConfiguration(
            **values,
        )


def test_runtime_configuration_rejects_boolean_seed() -> None:
    with pytest.raises(
        ValueError,
        match="random_seed must be an integer",
    ):
        ResearchRuntimeConfiguration(
            code_version="git:abc123",
            executor_version="backtest-engine:v1",
            statistical_method_version="statistics:v1",
            random_seed=True,
        )