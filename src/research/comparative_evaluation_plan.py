from __future__ import annotations

import json
from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256
from math import isfinite
from numbers import Real


class ExpectedEffectDirection(StrEnum):
    """
    Effect direction declared before results are analyzed.
    """

    POSITIVE = "positive"
    NEGATIVE = "negative"
    TWO_SIDED = "two_sided"


@dataclass(frozen=True, slots=True)
class ComparativeEvaluationPlan:
    """
    Predeclared statistical and replication evaluation rules.
    """

    expected_direction: ExpectedEffectDirection = (
        ExpectedEffectDirection.POSITIVE
    )
    method: str = "moving_block_bootstrap"
    confidence_level: float = 0.95
    resample_count: int = 2_000
    block_length: int = 24
    random_seed: int = 0
    minimum_candidate_sample_size: int = 30
    minimum_replication_count: int = 2
    minimum_supporting_replication_count: int = 2

    def __post_init__(self) -> None:
        if not isinstance(
            self.expected_direction,
            ExpectedEffectDirection,
        ):
            raise TypeError(
                "expected_direction must be an "
                "ExpectedEffectDirection"
            )

        method = self._normalize_text(
            self.method,
            field_name="method",
        )
        confidence_level = (
            self._require_confidence_level(
                self.confidence_level
            )
        )
        resample_count = self._require_positive_integer(
            self.resample_count,
            field_name="resample_count",
        )

        if resample_count < 2:
            raise ValueError(
                "resample_count must be at least 2"
            )

        block_length = self._require_positive_integer(
            self.block_length,
            field_name="block_length",
        )
        random_seed = (
            self._require_nonnegative_integer(
                self.random_seed,
                field_name="random_seed",
            )
        )
        minimum_candidate_sample_size = (
            self._require_positive_integer(
                self.minimum_candidate_sample_size,
                field_name=(
                    "minimum_candidate_sample_size"
                ),
            )
        )
        minimum_replication_count = (
            self._require_positive_integer(
                self.minimum_replication_count,
                field_name=(
                    "minimum_replication_count"
                ),
            )
        )
        minimum_supporting_replication_count = (
            self._require_positive_integer(
                self.minimum_supporting_replication_count,
                field_name=(
                    "minimum_supporting_replication_count"
                ),
            )
        )

        if (
            minimum_supporting_replication_count
            > minimum_replication_count
        ):
            raise ValueError(
                "minimum supporting replication count "
                "must not exceed minimum replication count"
            )

        object.__setattr__(
            self,
            "method",
            method,
        )
        object.__setattr__(
            self,
            "confidence_level",
            confidence_level,
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
            "minimum_candidate_sample_size",
            minimum_candidate_sample_size,
        )
        object.__setattr__(
            self,
            "minimum_replication_count",
            minimum_replication_count,
        )
        object.__setattr__(
            self,
            "minimum_supporting_replication_count",
            minimum_supporting_replication_count,
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": 1,
            "expected_direction": (
                self.expected_direction.value
            ),
            "method": self.method,
            "confidence_level": self.confidence_level,
            "resample_count": self.resample_count,
            "block_length": self.block_length,
            "random_seed": self.random_seed,
            "minimum_candidate_sample_size": (
                self.minimum_candidate_sample_size
            ),
            "minimum_replication_count": (
                self.minimum_replication_count
            ),
            "minimum_supporting_replication_count": (
                self.minimum_supporting_replication_count
            ),
        }

    @property
    def fingerprint(self) -> str:
        serialized = json.dumps(
            self.to_dict(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        )

        return sha256(
            serialized.encode("utf-8")
        ).hexdigest()

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
