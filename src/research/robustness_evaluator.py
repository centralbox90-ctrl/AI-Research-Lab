from collections.abc import Sequence
from numbers import Real
from statistics import mean
from typing import Any

from src.research.experiment_result import ExperimentResult
from src.research.robustness_evaluation import RobustnessEvaluation


class RobustnessEvaluator:
    """
    Выполняет оценку устойчивости результата эксперимента.

    По умолчанию использует raw observations из:

    result.observations["profit_percent"]

    Рассчитывает:

    - долю положительных наблюдений;
    - долю отрицательных наблюдений;
    - долю нулевых наблюдений;
    - среднее первой половины выборки;
    - среднее второй половины выборки;
    - изменение среднего между половинами;
    - согласованность направления средних;
    - решение об устойчивости результата.

    Текущее правило robustness:

    - направление средних первой и второй половины согласовано;
    - не менее 60% наблюдений имеют доминирующее ненулевое
      направление.

    Statistical significance не используется в robustness decision.
    """

    MIN_DOMINANT_DIRECTION_RATIO = 0.60

    def evaluate(
        self,
        result: ExperimentResult,
        observations: Sequence[Real] | None = None,
    ) -> RobustnessEvaluation:
        warnings: list[str] = []

        if not result.experiment_id:
            warnings.append("Experiment ID is missing")

        resolved_observations = self._resolve_observations(
            result=result,
            observations=observations,
        )

        if resolved_observations is None:
            warnings.append("Raw observations are missing")

            return RobustnessEvaluation(
                experiment_id=result.experiment_id,
                is_evaluated=False,
                is_robust=False,
                warnings=warnings,
                notes=(
                    "Robustness evaluation requires raw observations. "
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

            return RobustnessEvaluation(
                experiment_id=result.experiment_id,
                is_evaluated=False,
                is_robust=False,
                sample_size=0,
                warnings=warnings,
                notes=(
                    "Robustness diagnostics could not be calculated."
                ),
            )

        positive_count = sum(
            1 for value in numeric_observations if value > 0.0
        )
        negative_count = sum(
            1 for value in numeric_observations if value < 0.0
        )
        zero_count = sum(
            1 for value in numeric_observations if value == 0.0
        )

        positive_observation_ratio = (
            positive_count / sample_size
        )
        negative_observation_ratio = (
            negative_count / sample_size
        )
        zero_observation_ratio = (
            zero_count / sample_size
        )

        if sample_size < 2:
            warnings.append(
                "At least two numeric observations are required "
                "for split-sample diagnostics and robustness decision"
            )

            return RobustnessEvaluation(
                experiment_id=result.experiment_id,
                is_evaluated=True,
                is_robust=False,
                sample_size=sample_size,
                positive_observation_ratio=float(
                    positive_observation_ratio
                ),
                negative_observation_ratio=float(
                    negative_observation_ratio
                ),
                zero_observation_ratio=float(
                    zero_observation_ratio
                ),
                warnings=warnings,
                notes=(
                    "Observation direction ratios were calculated. "
                    "Split-sample diagnostics and robustness decision "
                    "require at least two observations."
                ),
            )

        split_index = sample_size // 2

        first_half = numeric_observations[:split_index]
        second_half = numeric_observations[split_index:]

        first_half_mean = float(mean(first_half))
        second_half_mean = float(mean(second_half))

        mean_shift = second_half_mean - first_half_mean

        direction_consistent = self._same_direction(
            first_half_mean,
            second_half_mean,
        )

        dominant_direction_ratio = max(
            positive_observation_ratio,
            negative_observation_ratio,
        )

        is_robust = (
            direction_consistent
            and dominant_direction_ratio
            >= self.MIN_DOMINANT_DIRECTION_RATIO
        )

        return RobustnessEvaluation(
            experiment_id=result.experiment_id,
            is_evaluated=True,
            is_robust=is_robust,
            sample_size=sample_size,
            positive_observation_ratio=float(
                positive_observation_ratio
            ),
            negative_observation_ratio=float(
                negative_observation_ratio
            ),
            zero_observation_ratio=float(
                zero_observation_ratio
            ),
            first_half_mean=first_half_mean,
            second_half_mean=second_half_mean,
            mean_shift=float(mean_shift),
            direction_consistent=direction_consistent,
            warnings=warnings,
            notes=(
                "Direction ratios and split-sample diagnostics were "
                "calculated. Robustness was evaluated using direction "
                "consistency and the dominant observation direction ratio."
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

    @staticmethod
    def _same_direction(
        first_value: float,
        second_value: float,
    ) -> bool:
        if first_value > 0.0 and second_value > 0.0:
            return True

        if first_value < 0.0 and second_value < 0.0:
            return True

        if first_value == 0.0 and second_value == 0.0:
            return True

        return False