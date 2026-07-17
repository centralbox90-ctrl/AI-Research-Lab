import pytest

from src.research.experiment_result import ExperimentResult
from src.research.statistical_evaluator import StatisticalEvaluator


def test_statistical_evaluator_requires_raw_observations() -> None:
    result = ExperimentResult(
        experiment_id="experiment-1",
        metrics={"net_profit": 8.0},
    )

    evaluation = StatisticalEvaluator().evaluate(result)

    assert evaluation.experiment_id == "experiment-1"
    assert evaluation.is_evaluated is False
    assert evaluation.is_significant is False

    assert evaluation.null_mean == 0.0
    assert evaluation.alternative == "two-sided"
    assert evaluation.significance_level == 0.05
    assert evaluation.test_method == "one-sample Student t-test"

    assert evaluation.test_statistic is None
    assert evaluation.p_value is None
    assert evaluation.effect_size is None

    assert "Raw observations are missing" in evaluation.warnings
    assert (
        evaluation.notes
        == (
            "Statistical evaluation requires raw observations. "
            "Aggregate metrics are insufficient."
        )
    )


def test_statistical_evaluator_calculates_descriptive_statistics() -> None:
    result = ExperimentResult(
        experiment_id="experiment-1",
        metrics={"net_profit": 8.0},
    )

    evaluation = StatisticalEvaluator().evaluate(
        result=result,
        observations=[1.5, -0.5, 2.0],
    )

    expected_mean = 1.0
    expected_standard_deviation = 1.3228756555322954
    expected_standard_error = (
        expected_standard_deviation / (3 ** 0.5)
    )
    expected_margin = 1.96 * expected_standard_error
    expected_test_statistic = (
        expected_mean / expected_standard_error
    )
    expected_effect_size = (
        expected_mean / expected_standard_deviation
    )
    expected_p_value = 0.3206337795132426

    assert evaluation.experiment_id == "experiment-1"
    assert evaluation.is_evaluated is True
    assert evaluation.is_significant is False
    assert evaluation.sample_size == 3

    assert evaluation.mean == pytest.approx(expected_mean)
    assert evaluation.standard_deviation == pytest.approx(
        expected_standard_deviation
    )
    assert evaluation.standard_error == pytest.approx(
        expected_standard_error
    )
    assert evaluation.confidence_interval_lower == pytest.approx(
        expected_mean - expected_margin
    )
    assert evaluation.confidence_interval_upper == pytest.approx(
        expected_mean + expected_margin
    )
    assert evaluation.confidence_level == 0.95

    assert evaluation.null_mean == 0.0
    assert evaluation.alternative == "two-sided"
    assert evaluation.significance_level == 0.05
    assert evaluation.test_method == "one-sample Student t-test"

    assert evaluation.test_statistic == pytest.approx(
        expected_test_statistic
    )
    assert evaluation.p_value == pytest.approx(
        expected_p_value
    )
    assert evaluation.effect_size == pytest.approx(
        expected_effect_size
    )

    assert evaluation.warnings == []

    assert (
        evaluation.notes
        == (
            "Descriptive statistics, a 95% confidence interval "
            "using a normal approximation, a one-sample "
            "t-statistic, a two-sided p-value and Cohen's d "
            "were calculated. Statistical significance was "
            "evaluated against the configured significance level."
        )
    )


def test_statistical_evaluator_reads_observations_from_result() -> None:
    result = ExperimentResult(
        experiment_id="experiment-1",
        metrics={"net_profit": 8.0},
        observations={
            "profit_percent": [1.0, 2.0, 3.0],
        },
    )

    evaluation = StatisticalEvaluator().evaluate(result)

    expected_standard_error = 1.0 / (3 ** 0.5)
    expected_margin = 1.96 * expected_standard_error
    expected_test_statistic = 2.0 / expected_standard_error
    expected_p_value = 0.07417990022744857
    expected_effect_size = 2.0

    assert evaluation.is_evaluated is True
    assert evaluation.is_significant is False
    assert evaluation.sample_size == 3

    assert evaluation.mean == pytest.approx(2.0)
    assert evaluation.standard_deviation == pytest.approx(1.0)
    assert evaluation.standard_error == pytest.approx(
        expected_standard_error
    )
    assert evaluation.confidence_interval_lower == pytest.approx(
        2.0 - expected_margin
    )
    assert evaluation.confidence_interval_upper == pytest.approx(
        2.0 + expected_margin
    )
    assert evaluation.confidence_level == 0.95

    assert evaluation.null_mean == 0.0
    assert evaluation.alternative == "two-sided"
    assert evaluation.significance_level == 0.05
    assert evaluation.test_method == "one-sample Student t-test"

    assert evaluation.test_statistic == pytest.approx(
        expected_test_statistic
    )
    assert evaluation.p_value == pytest.approx(
        expected_p_value
    )
    assert evaluation.effect_size == pytest.approx(
        expected_effect_size
    )

    assert evaluation.warnings == []


def test_statistical_evaluator_handles_zero_standard_error() -> None:
    result = ExperimentResult(
        experiment_id="experiment-1",
        metrics={"net_profit": 3.0},
    )

    evaluation = StatisticalEvaluator().evaluate(
        result=result,
        observations=[1.0, 1.0, 1.0],
    )

    assert evaluation.is_evaluated is True
    assert evaluation.is_significant is False

    assert evaluation.mean == pytest.approx(1.0)
    assert evaluation.standard_deviation == pytest.approx(0.0)
    assert evaluation.standard_error == pytest.approx(0.0)

    assert evaluation.test_method == "one-sample Student t-test"
    assert evaluation.test_statistic is None
    assert evaluation.p_value is None
    assert evaluation.effect_size is None

    assert (
        "Test statistic and p-value cannot be calculated because "
        "the standard error is zero"
    ) in evaluation.warnings

    assert (
        "Effect size cannot be calculated because "
        "the standard deviation is zero"
    ) in evaluation.warnings


def test_statistical_evaluator_detects_significant_result() -> None:
    result = ExperimentResult(
        experiment_id="experiment-1",
        metrics={"net_profit": 5.0},
    )

    evaluation = StatisticalEvaluator().evaluate(
        result=result,
        observations=[1.8, 2.0, 2.1, 1.9, 2.2],
    )

    assert evaluation.is_evaluated is True
    assert evaluation.p_value is not None
    assert evaluation.p_value < evaluation.significance_level
    assert evaluation.is_significant is True

    assert evaluation.test_statistic is not None
    assert evaluation.effect_size is not None