from __future__ import annotations

from math import isfinite
from numbers import Real

import numpy as np

from src.research.comparative_analysis import (
    ComparativeAnalysis,
)
from src.research.comparative_statistical_evaluation import (
    ComparativeStatisticalEvaluation,
)
from src.research.horizon_comparison import (
    HorizonComparison,
)


class ComparativeStatisticalEvaluator:
    """
    Estimates uncertainty with a deterministic moving-block bootstrap.
    """

    _METHOD = "moving_block_bootstrap"

    def evaluate(
        self,
        *,
        analysis: ComparativeAnalysis,
        research_fingerprint: str,
        dataset_id: str,
        confidence_level: float = 0.95,
        resample_count: int = 2_000,
        block_length: int = 24,
        random_seed: int = 0,
    ) -> tuple[
        ComparativeStatisticalEvaluation,
        ...,
    ]:
        if not isinstance(
            analysis,
            ComparativeAnalysis,
        ):
            raise TypeError(
                "analysis must be a ComparativeAnalysis"
            )

        normalized_research_fingerprint = (
            self._normalize_text(
                research_fingerprint,
                field_name="research_fingerprint",
            )
        )
        normalized_dataset_id = self._normalize_text(
            dataset_id,
            field_name="dataset_id",
        )
        normalized_confidence_level = (
            self._require_confidence_level(
                confidence_level
            )
        )
        normalized_resample_count = (
            self._require_resample_count(
                resample_count
            )
        )
        normalized_block_length = (
            self._require_positive_integer(
                block_length,
                field_name="block_length",
            )
        )
        normalized_random_seed = (
            self._require_nonnegative_integer(
                random_seed,
                field_name="random_seed",
            )
        )

        evaluations: list[
            ComparativeStatisticalEvaluation
        ] = []

        for comparison in analysis.comparisons:
            (
                baseline_returns,
                candidate_mask,
            ) = self._build_horizon_series(
                analysis=analysis,
                comparison=comparison,
            )

            if (
                normalized_block_length
                > len(baseline_returns)
            ):
                raise ValueError(
                    "block_length must not exceed "
                    "the baseline sample size"
                )

            bootstrap_effects, discarded_count = (
                self._bootstrap_effects(
                    baseline_returns=baseline_returns,
                    candidate_mask=candidate_mask,
                    horizon=comparison.horizon,
                    resample_count=(
                        normalized_resample_count
                    ),
                    block_length=(
                        normalized_block_length
                    ),
                    random_seed=(
                        normalized_random_seed
                    ),
                )
            )

            alpha = (
                1.0
                - normalized_confidence_level
            ) / 2.0
            lower, upper = np.quantile(
                bootstrap_effects,
                (
                    alpha,
                    1.0 - alpha,
                ),
                method="linear",
            )

            warnings = self._build_warnings(
                candidate_sample_size=(
                    comparison.candidate_sample_size
                ),
                discarded_count=discarded_count,
            )

            evaluations.append(
                ComparativeStatisticalEvaluation(
                    research_fingerprint=(
                        normalized_research_fingerprint
                    ),
                    dataset_id=normalized_dataset_id,
                    horizon=comparison.horizon,
                    candidate_sample_size=(
                        comparison.candidate_sample_size
                    ),
                    baseline_sample_size=(
                        comparison.baseline_sample_size
                    ),
                    effect_estimate=(
                        comparison.mean_return_difference
                    ),
                    confidence_interval_lower=float(
                        lower
                    ),
                    confidence_interval_upper=float(
                        upper
                    ),
                    confidence_level=(
                        normalized_confidence_level
                    ),
                    method=self._METHOD,
                    resample_count=(
                        normalized_resample_count
                    ),
                    block_length=(
                        normalized_block_length
                    ),
                    random_seed=(
                        normalized_random_seed
                    ),
                    warnings=warnings,
                )
            )

        return tuple(evaluations)

    @staticmethod
    def _build_horizon_series(
        *,
        analysis: ComparativeAnalysis,
        comparison: HorizonComparison,
    ) -> tuple[np.ndarray, np.ndarray]:
        horizon = comparison.horizon
        candidate_by_bar: dict[int, float] = {}
        baseline_by_bar: dict[int, float] = {}

        for outcome in (
            analysis.candidate_result.outcomes
        ):
            if outcome.horizon != horizon:
                continue

            if (
                outcome.start_bar_index
                in candidate_by_bar
            ):
                raise ValueError(
                    "candidate outcomes must have "
                    "unique start bar indexes"
                )

            candidate_by_bar[
                outcome.start_bar_index
            ] = outcome.value

        for outcome in (
            analysis.baseline_result.outcomes
        ):
            if outcome.horizon != horizon:
                continue

            if (
                outcome.start_bar_index
                in baseline_by_bar
            ):
                raise ValueError(
                    "baseline outcomes must have "
                    "unique start bar indexes"
                )

            baseline_by_bar[
                outcome.start_bar_index
            ] = outcome.value

        if (
            len(candidate_by_bar)
            != comparison.candidate_sample_size
        ):
            raise ValueError(
                "candidate outcomes must match "
                "candidate_sample_size"
            )

        if (
            len(baseline_by_bar)
            != comparison.baseline_sample_size
        ):
            raise ValueError(
                "baseline outcomes must match "
                "baseline_sample_size"
            )

        ordered_bars = tuple(
            sorted(baseline_by_bar)
        )
        baseline_returns = np.asarray(
            tuple(
                baseline_by_bar[bar_index]
                for bar_index in ordered_bars
            ),
            dtype=float,
        )
        candidate_mask = np.zeros(
            len(ordered_bars),
            dtype=bool,
        )
        baseline_position_by_bar = {
            bar_index: position
            for position, bar_index in enumerate(
                ordered_bars
            )
        }

        for (
            bar_index,
            candidate_return,
        ) in candidate_by_bar.items():
            baseline_position = (
                baseline_position_by_bar.get(
                    bar_index
                )
            )

            if baseline_position is None:
                raise ValueError(
                    "each candidate outcome must align "
                    "with a baseline outcome"
                )

            baseline_return = baseline_returns[
                baseline_position
            ]

            if not np.isclose(
                candidate_return,
                baseline_return,
                rtol=1e-12,
                atol=1e-15,
            ):
                raise ValueError(
                    "aligned candidate and baseline "
                    "returns must be equal"
                )

            candidate_mask[
                baseline_position
            ] = True

        calculated_effect = float(
            baseline_returns[candidate_mask].mean()
            - baseline_returns.mean()
        )

        if not np.isclose(
            calculated_effect,
            comparison.mean_return_difference,
            rtol=1e-12,
            atol=1e-15,
        ):
            raise ValueError(
                "comparison mean return difference "
                "must match its outcomes"
            )

        return baseline_returns, candidate_mask

    @staticmethod
    def _bootstrap_effects(
        *,
        baseline_returns: np.ndarray,
        candidate_mask: np.ndarray,
        horizon: int,
        resample_count: int,
        block_length: int,
        random_seed: int,
    ) -> tuple[np.ndarray, int]:
        sample_size = len(baseline_returns)
        block_count = (
            sample_size + block_length - 1
        ) // block_length
        maximum_start = (
            sample_size - block_length
        )
        random_generator = np.random.default_rng(
            np.random.SeedSequence(
                [
                    random_seed,
                    horizon,
                ]
            )
        )
        offsets = np.arange(
            block_length,
            dtype=int,
        )
        effects = np.empty(
            resample_count,
            dtype=float,
        )
        completed_count = 0
        discarded_count = 0
        attempt_count = 0
        maximum_attempt_count = max(
            100,
            resample_count * 100,
        )

        while (
            completed_count < resample_count
            and attempt_count < maximum_attempt_count
        ):
            attempt_count += 1
            starts = random_generator.integers(
                0,
                maximum_start + 1,
                size=block_count,
            )
            sampled_indexes = (
                starts[:, None] + offsets
            ).reshape(-1)[:sample_size]
            sampled_candidate_mask = (
                candidate_mask[sampled_indexes]
            )

            if not sampled_candidate_mask.any():
                discarded_count += 1
                continue

            sampled_returns = baseline_returns[
                sampled_indexes
            ]
            effects[completed_count] = (
                sampled_returns[
                    sampled_candidate_mask
                ].mean()
                - sampled_returns.mean()
            )
            completed_count += 1

        if completed_count != resample_count:
            raise ValueError(
                "unable to produce enough bootstrap "
                "resamples containing candidate observations"
            )

        return effects, discarded_count

    @staticmethod
    def _build_warnings(
        *,
        candidate_sample_size: int,
        discarded_count: int,
    ) -> tuple[str, ...]:
        warnings: list[str] = []

        if candidate_sample_size < 30:
            warnings.append(
                "candidate sample size is below 30"
            )

        if discarded_count:
            warnings.append(
                "bootstrap resamples without candidate "
                "observations were discarded"
            )

        return tuple(warnings)

    @staticmethod
    def _normalize_text(
        value: object,
        *,
        field_name: str,
    ) -> str:
        if not isinstance(value, str):
            raise TypeError(
                f"{field_name} must be a string"
            )

        normalized = value.strip()

        if not normalized:
            raise ValueError(
                f"{field_name} must not be empty"
            )

        return normalized

    @staticmethod
    def _require_positive_integer(
        value: object,
        *,
        field_name: str,
    ) -> int:
        if (
            not isinstance(value, int)
            or isinstance(value, bool)
        ):
            raise TypeError(
                f"{field_name} must be an integer"
            )

        if value < 1:
            raise ValueError(
                f"{field_name} must be positive"
            )

        return value

    @classmethod
    def _require_resample_count(
        cls,
        value: object,
    ) -> int:
        normalized = cls._require_positive_integer(
            value,
            field_name="resample_count",
        )

        if normalized < 2:
            raise ValueError(
                "resample_count must be at least 2"
            )

        return normalized

    @staticmethod
    def _require_nonnegative_integer(
        value: object,
        *,
        field_name: str,
    ) -> int:
        if (
            not isinstance(value, int)
            or isinstance(value, bool)
        ):
            raise TypeError(
                f"{field_name} must be an integer"
            )

        if value < 0:
            raise ValueError(
                f"{field_name} must not be negative"
            )

        return value

    @staticmethod
    def _require_confidence_level(
        value: object,
    ) -> float:
        if (
            not isinstance(value, Real)
            or isinstance(value, bool)
        ):
            raise TypeError(
                "confidence_level must be a real number"
            )

        normalized = float(value)

        if not isfinite(normalized):
            raise ValueError(
                "confidence_level must be finite"
            )

        if not 0.0 < normalized < 1.0:
            raise ValueError(
                "confidence_level must be between 0 and 1"
            )

        return normalized
