from __future__ import annotations

import json
from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256
from math import isfinite
from numbers import Real


class HypothesisEvaluationState(StrEnum):
    """Scientific state assigned to an evaluated hypothesis."""

    SUPPORTED = "supported"
    PARTIALLY_SUPPORTED = "partially_supported"
    INCONCLUSIVE = "inconclusive"
    REJECTED = "rejected"


@dataclass(frozen=True, slots=True)
class HypothesisEvaluation:
    """
    Immutable result of evaluating one hypothesis from Findings.
    """

    id: str
    hypothesis_id: str
    state: HypothesisEvaluationState
    confidence: float
    finding_refs: tuple[str, ...]
    rationale: tuple[str, ...]
    provenance: tuple[
        tuple[str, str],
        ...,
    ]
    limitations: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        evaluation_id = self._normalize_text(
            self.id,
            field_name="id",
        )
        hypothesis_id = self._normalize_text(
            self.hypothesis_id,
            field_name="hypothesis_id",
        )

        if not isinstance(
            self.state,
            HypothesisEvaluationState,
        ):
            raise TypeError(
                "state must be a "
                "HypothesisEvaluationState"
            )

        confidence = self._normalize_confidence(
            self.confidence
        )
        finding_refs = self._normalize_text_items(
            self.finding_refs,
            field_name="finding_refs",
            require_nonempty=True,
        )
        rationale = self._normalize_text_items(
            self.rationale,
            field_name="rationale",
            require_nonempty=True,
        )
        limitations = self._normalize_text_items(
            self.limitations,
            field_name="limitations",
        )
        provenance = self._normalize_provenance(
            self.provenance
        )

        object.__setattr__(
            self,
            "id",
            evaluation_id,
        )
        object.__setattr__(
            self,
            "hypothesis_id",
            hypothesis_id,
        )
        object.__setattr__(
            self,
            "confidence",
            confidence,
        )
        object.__setattr__(
            self,
            "finding_refs",
            finding_refs,
        )
        object.__setattr__(
            self,
            "rationale",
            rationale,
        )
        object.__setattr__(
            self,
            "limitations",
            limitations,
        )
        object.__setattr__(
            self,
            "provenance",
            provenance,
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": 1,
            "id": self.id,
            "hypothesis_id": self.hypothesis_id,
            "state": self.state.value,
            "confidence": self.confidence,
            "finding_refs": list(
                self.finding_refs
            ),
            "rationale": list(
                self.rationale
            ),
            "limitations": list(
                self.limitations
            ),
            "provenance": {
                key: value
                for key, value in self.provenance
            },
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

    @classmethod
    def _normalize_text_items(
        cls,
        values: object,
        *,
        field_name: str,
        require_nonempty: bool = False,
    ) -> tuple[str, ...]:
        if not isinstance(values, tuple):
            raise TypeError(
                f"{field_name} must be a tuple"
            )

        if require_nonempty and not values:
            raise ValueError(
                f"{field_name} must not be empty"
            )

        normalized = tuple(
            cls._normalize_text(
                value,
                field_name=field_name,
            )
            for value in values
        )

        if len(normalized) != len(set(normalized)):
            raise ValueError(
                f"{field_name} must not contain duplicates"
            )

        return tuple(sorted(normalized))

    @staticmethod
    def _normalize_confidence(
        value: object,
    ) -> float:
        if (
            not isinstance(value, Real)
            or isinstance(value, bool)
        ):
            raise TypeError(
                "confidence must be a real number"
            )

        normalized = float(value)

        if not isfinite(normalized):
            raise ValueError(
                "confidence must be finite"
            )

        if not 0.0 <= normalized <= 1.0:
            raise ValueError(
                "confidence must be between 0 and 1"
            )

        return normalized

    @classmethod
    def _normalize_provenance(
        cls,
        value: object,
    ) -> tuple[
        tuple[str, str],
        ...,
    ]:
        if not isinstance(value, tuple):
            raise TypeError(
                "provenance must be a tuple"
            )

        if not value:
            raise ValueError(
                "provenance must not be empty"
            )

        normalized: list[
            tuple[str, str]
        ] = []

        for entry in value:
            if (
                not isinstance(entry, tuple)
                or len(entry) != 2
            ):
                raise TypeError(
                    "each provenance entry must be "
                    "a key-value tuple"
                )

            key = cls._normalize_text(
                entry[0],
                field_name="provenance key",
            )
            item = cls._normalize_text(
                entry[1],
                field_name="provenance value",
            )
            normalized.append((key, item))

        keys = tuple(
            key
            for key, _ in normalized
        )

        if len(keys) != len(set(keys)):
            raise ValueError(
                "provenance keys must be unique"
            )

        return tuple(sorted(normalized))