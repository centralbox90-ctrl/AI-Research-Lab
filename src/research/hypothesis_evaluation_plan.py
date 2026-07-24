from __future__ import annotations

import json
from dataclasses import dataclass
from hashlib import sha256
from math import isfinite
from numbers import Real


@dataclass(frozen=True, slots=True)
class HypothesisEvaluationPlan:
    """
    Predeclared rules for evaluating Findings into a hypothesis state.
    """

    version: str = "hypothesis-evaluation-v1"
    supported_confidence_threshold: float = 0.75
    partially_supported_confidence_threshold: float = 0.5
    rejected_confidence_threshold: float = 0.75
    minimum_decisive_findings: int = 2

    def __post_init__(self) -> None:
        version = self._normalize_text(
            self.version,
            field_name="version",
        )
        supported_threshold = self._normalize_score(
            self.supported_confidence_threshold,
            field_name=(
                "supported_confidence_threshold"
            ),
        )
        partially_supported_threshold = (
            self._normalize_score(
                self.partially_supported_confidence_threshold,
                field_name=(
                    "partially_supported_confidence_threshold"
                ),
            )
        )
        rejected_threshold = self._normalize_score(
            self.rejected_confidence_threshold,
            field_name=(
                "rejected_confidence_threshold"
            ),
        )
        minimum_decisive_findings = (
            self._normalize_positive_integer(
                self.minimum_decisive_findings,
                field_name=(
                    "minimum_decisive_findings"
                ),
            )
        )

        if (
            partially_supported_threshold
            > supported_threshold
        ):
            raise ValueError(
                "partially_supported_confidence_threshold "
                "must not exceed "
                "supported_confidence_threshold"
            )

        object.__setattr__(
            self,
            "version",
            version,
        )
        object.__setattr__(
            self,
            "supported_confidence_threshold",
            supported_threshold,
        )
        object.__setattr__(
            self,
            "partially_supported_confidence_threshold",
            partially_supported_threshold,
        )
        object.__setattr__(
            self,
            "rejected_confidence_threshold",
            rejected_threshold,
        )
        object.__setattr__(
            self,
            "minimum_decisive_findings",
            minimum_decisive_findings,
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": 1,
            "version": self.version,
            "supported_confidence_threshold": (
                self.supported_confidence_threshold
            ),
            "partially_supported_confidence_threshold": (
                self.partially_supported_confidence_threshold
            ),
            "rejected_confidence_threshold": (
                self.rejected_confidence_threshold
            ),
            "minimum_decisive_findings": (
                self.minimum_decisive_findings
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
    def _normalize_score(
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

        if not 0.0 <= normalized <= 1.0:
            raise ValueError(
                f"{field_name} must be between 0 and 1"
            )

        return normalized

    @staticmethod
    def _normalize_positive_integer(
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
                f"{field_name} must be at least 1"
            )

        return value