from __future__ import annotations

import json
from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256
from math import isfinite
from numbers import Real


class EvidenceDirection(StrEnum):
    """Relationship between evidence and its hypothesis."""

    SUPPORTING = "supporting"
    CONTRADICTORY = "contradictory"
    INCONCLUSIVE = "inconclusive"


class EvidenceStrength(StrEnum):
    """Predefined qualitative evidence strength."""

    NONE = "none"
    WEAK = "weak"
    MODERATE = "moderate"
    STRONG = "strong"


@dataclass(frozen=True, slots=True)
class Evidence:
    """
    Immutable, reproducible assessment of one hypothesis.
    """

    id: str
    hypothesis_id: str
    observation_refs: tuple[str, ...]
    direction: EvidenceDirection
    strength: EvidenceStrength
    confidence: float
    consistency: float
    robustness: float
    provenance: tuple[
        tuple[str, str],
        ...,
    ]
    applicability: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        evidence_id = self._normalize_text(
            self.id,
            field_name="id",
        )
        hypothesis_id = self._normalize_text(
            self.hypothesis_id,
            field_name="hypothesis_id",
        )
        observation_refs = self._normalize_text_items(
            self.observation_refs,
            field_name="observation_refs",
            require_nonempty=True,
        )

        if not isinstance(
            self.direction,
            EvidenceDirection,
        ):
            raise TypeError(
                "direction must be an EvidenceDirection"
            )

        if not isinstance(
            self.strength,
            EvidenceStrength,
        ):
            raise TypeError(
                "strength must be an EvidenceStrength"
            )

        confidence = self._normalize_score(
            self.confidence,
            field_name="confidence",
        )
        consistency = self._normalize_score(
            self.consistency,
            field_name="consistency",
        )
        robustness = self._normalize_score(
            self.robustness,
            field_name="robustness",
        )
        applicability = self._normalize_text_items(
            self.applicability,
            field_name="applicability",
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
            evidence_id,
        )
        object.__setattr__(
            self,
            "hypothesis_id",
            hypothesis_id,
        )
        object.__setattr__(
            self,
            "observation_refs",
            observation_refs,
        )
        object.__setattr__(
            self,
            "confidence",
            confidence,
        )
        object.__setattr__(
            self,
            "consistency",
            consistency,
        )
        object.__setattr__(
            self,
            "robustness",
            robustness,
        )
        object.__setattr__(
            self,
            "applicability",
            applicability,
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
            "observation_refs": list(
                self.observation_refs
            ),
            "direction": self.direction.value,
            "strength": self.strength.value,
            "confidence": self.confidence,
            "consistency": self.consistency,
            "robustness": self.robustness,
            "applicability": list(
                self.applicability
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
            normalized.append(
                (
                    key,
                    item,
                )
            )

        keys = tuple(
            key
            for key, _ in normalized
        )

        if len(keys) != len(set(keys)):
            raise ValueError(
                "provenance keys must be unique"
            )

        return tuple(
            sorted(
                normalized,
                key=lambda entry: entry[0],
            )
        )
