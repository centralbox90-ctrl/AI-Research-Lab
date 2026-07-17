from collections.abc import Sequence
from math import sqrt
from numbers import Real
from statistics import mean, stdev
from typing import Any

from scipy.stats import t

from src.research.experiment_result import ExperimentResult
from src.research.statistical_evaluation import StatisticalEvaluation


class StatisticalEvaluator:
    """
    Выполняет статистическую оценку результата эксперимента.

    По умолчанию использует raw observations из:

    result.observations["profit_percent"]

    Текущая версия вычисляет:

    - размер выборки;
    - среднее значение;
    - выборочное стандартное отклонение;
    - стандартную ошибку среднего;
    - 95% доверительный интервал по нормальному приближению;
    - test statistic для one-sample Student t-test;
    - двусторонний p-value;
    - effect size как one-sample Cohen's d;
    - решение о statistical significance.

    Inferential постановка:

    H0: среднее значение observations равно 0.
    H1: среднее значение observations не равно 0.

    Statistical significance является только inferential signal
    и не означает автоматического подтверждения research hypothesis.
    """

    CONFIDENCE_LEVEL = 0.95
    NORMAL_CRITICAL_VALUE = 1.96

    NULL_MEAN = 0.0
    ALTERNATIVE = "two-sided"
    SIGNIFICANCE_LEVEL = 0.05
    TEST_METHOD = "one-sample Student t-test"

    def evaluate(
        self,
        result: ExperimentResult,
        observations: Sequence[Real] | None = None,
    ) -> StatisticalEvaluation:
        warnings: list[str] = []

        if not result.experiment_id:
            warnings.append("Experiment ID is missing")

        resolved_observations = self._resolve_observations(
            result=result,
            observations=observations,
        )

        if resolved_observations is None:
            warnings.append("Raw observations are missing")

            return StatisticalEvaluation(
                experiment_id=result.experiment_id,
                is_evaluated=False,
                is_significant=False,
                null_mean=self.NULL_MEAN,
                alternative=self.ALTERNATIVE,
                significance_level=self.SIGNIFICANCE_LEVEL,
                test_method=self.TEST_METHOD,
                warnings=warnings,
                notes=(
                    "Statistical evaluation requires raw observations. "
                    "Aggregate metrics are insufficient."
                ),
            )

        numeric_observations = [
            float(value)
            for value in resolved_observations
            if not isinstance(value, bool)
            and isinstance(value, Real)
        ]

        if len(numeric_observations) != len(resolved_observations):
            warnings.append(
                "Observations contain non-numeric values"
            )

        sample_size = len(numeric_observations)

        if sample_size == 0:
            warnings.append(
                "At least one numeric observation is required"
            )

            return StatisticalEvaluation(
                experiment_id=result.experiment_id,
                is_evaluated=False,
                is_significant=False,
                null_mean=self.NULL_MEAN,
                alternative=self.ALTERNATIVE,
                significance_level=self.SIGNIFICANCE_LEVEL,
                test_method=self.TEST_METHOD,
                sample_size=0,
                warnings=warnings,
                notes=(
                    "Descriptive statistics could not be calculated."
                ),
            )

        average = float(mean(numeric_observations))

        if sample_size < 2:
            warnings.append(
                "At least two numeric observations are required "
                "for uncertainty and inferential estimation"
            )

            return StatisticalEvaluation(
                experiment_id=result.experiment_id,
                is_evaluated=True,
                is_significant=False,
                mean=average,
                null_mean=self.NULL_MEAN,
                alternative=self.ALTERNATIVE,
                significance_level=self.SIGNIFICANCE_LEVEL,
                test_method=self.TEST_METHOD,
                sample_size=sample_size,
                warnings=warnings,
                notes=(
                    "Mean calculated. Standard deviation, standard error, "
                    "confidence interval, test statistic, p-value and "
                    "effect size require at least two observations."
                ),
            )

        standard_deviation = float(
            stdev(numeric_observations)
        )

        standard_error = (
            standard_deviation / sqrt(sample_size)
        )

        margin_of_error = (
            self.NORMAL_CRITICAL_VALUE * standard_error
        )

        confidence_interval_lower = (
            average - margin_of_error
        )

        confidence_interval_upper = (
            average + margin_of_error
        )

        test_statistic: float | None = None
        p_value: float | None = None
        effect_size: float | None = None
        is_significant = False

        if standard_error > 0.0:
            test_statistic = (
                average - self.NULL_MEAN
            ) / standard_error

            degrees_of_freedom = sample_size - 1

            p_value = 2.0 * float(
                t.sf(
                    abs(test_statistic),
                    df=degrees_of_freedom,
                )
            )

            is_significant = (
                p_value < self.SIGNIFICANCE_LEVEL
            )
        else:
            warnings.append(
                "Test statistic and p-value cannot be calculated "
                "because the standard error is zero"
            )

        if standard_deviation > 0.0:
            effect_size = (
                average - self.NULL_MEAN
            ) / standard_deviation
        else:
            warnings.append(
                "Effect size cannot be calculated because "
                "the standard deviation is zero"
            )

        return StatisticalEvaluation(
            experiment_id=result.experiment_id,
            is_evaluated=True,
            is_significant=is_significant,
            mean=average,
            standard_deviation=standard_deviation,
            standard_error=float(standard_error),
            confidence_interval_lower=float(
                confidence_interval_lower
            ),
            confidence_interval_upper=float(
                confidence_interval_upper
            ),
            confidence_level=self.CONFIDENCE_LEVEL,
            null_mean=self.NULL_MEAN,
            alternative=self.ALTERNATIVE,
            significance_level=self.SIGNIFICANCE_LEVEL,
            test_method=self.TEST_METHOD,
            test_statistic=(
                float(test_statistic)
                if test_statistic is not None
                else None
            ),
            p_value=(
                float(p_value)
                if p_value is not None
                else None
            ),
            effect_size=(
                float(effect_size)
                if effect_size is not None
                else None
            ),
            sample_size=sample_size,
            warnings=warnings,
            notes=(
                "Descriptive statistics, a 95% confidence interval "
                "using a normal approximation, a one-sample "
                "t-statistic, a two-sided p-value and Cohen's d "
                "were calculated. Statistical significance was "
                "evaluated against the configured significance level."
            ),
        )

    def _resolve_observations(
        self,
        result: ExperimentResult,
        observations: Sequence[Real] | None,
    ) -> Sequence[Any] | None:
        if observations is not None:
            return observations

        stored_observations = result.observations.get(
            "profit_percent"
        )

        if (
            isinstance(stored_observations, Sequence)
            and not isinstance(stored_observations, (str, bytes))
        ):
            return stored_observations

        return None