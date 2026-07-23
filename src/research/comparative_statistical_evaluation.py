from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from numbers import Real


@dataclass(frozen=True, slots=True)
class ComparativeStatisticalEvaluation:
    """
    Reproducible uncertainty estimate for one comparison horizon.
    """

    research_fingerprint: str
    dataset_id: str
    horizon: int
    candidate_sample_size: int
    baseline_sample_size: int
    effect_estimate: float
    confidence_interval_lower: float
    confidence_interval_upper: float
    confidence_level: float
    method: str
    resample_count: int
    block_length: int
    random_seed: int
    warnings: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        research_fingerprint = self._normalize_text(
            self.research_fingerprint,
            field_name="research_fingerprint",
        )
        dataset_id = self._normalize_text(
            self.dataset_id,
            field_name="dataset_id",
        )
        method = self._normalize_text(
            self.method,
            field_name="method",
        )

        horizon = self._require_positive_integer(
            self.horizon,
            field_name="horizon",
        )
        candidate_sample_size = (
            self._require_positive_integer(
                self.candidate_sample_size,
                field_name="candidate_sample_size",
            )
        )
        baseline_sample_size = (
            self._require_positive_integer(
                self.baseline_sample_size,
                field_name="baseline_sample_size",
            )
        )

        if candidate_sample_size > baseline_sample_size:
            raise ValueError(
                "candidate_sample_size must not exceed "
                "baseline_sample_size"
            )

        effect_estimate = self._require_finite_real(
            self.effect_estimate,
            field_name="effect_estimate",
        )
        confidence_interval_lower = (
            self._require_finite_real(
                self.confidence_interval_lower,
                field_name="confidence_interval_lower",
            )
        )
        confidence_interval_upper = (
            self._require_finite_real(
                self.confidence_interval_upper,
                field_name="confidence_interval_upper",
            )
        )
        confidence_level = self._require_finite_real(
            self.confidence_level,
            field_name="confidence_level",
        )

        if not 0.0 < confidence_level < 1.0:
            raise ValueError(
                "confidence_level must be between 0 and 1"
            )

        if (
            confidence_interval_lower
            > confidence_interval_upper
        ):
            raise ValueError(
                "confidence interval lower bound must not "
                "exceed its upper bound"
            )

        resample_count = self._require_positive_integer(
            self.resample_count,
            field_name="resample_count",
        )
        block_length = self._require_positive_integer(
            self.block_length,
            field_name="block_length",
        )

        if block_length > baseline_sample_size:
            raise ValueError(
                "block_length must not exceed "
                "baseline_sample_size"
            )

        random_seed = self._require_nonnegative_integer(
            self.random_seed,
            field_name="random_seed",
        )
        warnings = self._normalize_warnings(
            self.warnings
        )

        object.__setattr__(
            self,
            "research_fingerprint",
            research_fingerprint,
        )
        object.__setattr__(
            self,
            "dataset_id",
            dataset_id,
        )
        object.__setattr__(
            self,
            "horizon",
            horizon,
        )
        object.__setattr__(
            self,
            "candidate_sample_size",
            candidate_sample_size,
        )
        object.__setattr__(
            self,
            "baseline_sample_size",
            baseline_sample_size,
        )
        object.__setattr__(
            self,
            "effect_estimate",
            effect_estimate,
        )
        object.__setattr__(
            self,
            "confidence_interval_lower",
            confidence_interval_lower,
        )
        object.__setattr__(
            self,
            "confidence_interval_upper",
            confidence_interval_upper,
        )
        object.__setattr__(
            self,
            "confidence_level",
            confidence_level,
        )
        object.__setattr__(
            self,
            "method",
            method,
        )
        object.__setattr__(
            self,
            "resample_count",
            resample_count,
        )
        object.__setattr__(
            self,
            "block_length",
            block_length,
        )
        object.__setattr__(
            self,
            "random_seed",
            random_seed,
        )
        object.__setattr__(
            self,
            "warnings",
            warnings,
        )

    @property
    def excludes_zero(self) -> bool:
        return (
            self.confidence_interval_lower > 0.0
            or self.confidence_interval_upper < 0.0
        )

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
    def _require_finite_real(
        value: object,
        *,
        field_name: str,
    ) -> float:
        if (
            not isinstance(value, Real)
            or isinstance(value, bool)
        ):
            raise TypeError(
                f"{field_name} must be a real number"
            )

        normalized = float(value)

        if not isfinite(normalized):
            raise ValueError(
                f"{field_name} must be finite"
            )

        return normalized

    @classmethod
    def _normalize_warnings(
        cls,
        value: object,
    ) -> tuple[str, ...]:
        if not isinstance(value, tuple):
            raise TypeError(
                "warnings must be a tuple"
            )

        return tuple(
            cls._normalize_text(
                warning,
                field_name="each warning",
            )
            for warning in value
        )
