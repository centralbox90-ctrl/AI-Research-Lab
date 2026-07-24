from __future__ import annotations

import json
from dataclasses import dataclass
from hashlib import sha256
from typing import ClassVar


@dataclass(frozen=True, slots=True)
class CampaignDesign:
    """
    Immutable dimensions of a reproducible research campaign.

    All calculation, signal, execution, baseline, and data-period
    values are opaque references. CampaignDesign selects them but
    does not implement their behavior.
    """

    question_id: str
    hypothesis_ids: tuple[str, ...]
    instruments: tuple[str, ...]
    timeframes: tuple[str, ...]
    data_periods: tuple[str, ...]
    indicator_configurations: tuple[str, ...]
    signal_rules: tuple[str, ...]
    execution_policies: tuple[str, ...]
    baselines: tuple[str, ...]
    validation_strategy: str
    evaluation_plan_ref: str
    provenance: tuple[
        tuple[str, str],
        ...,
    ]

    SCHEMA_VERSION: ClassVar[int] = 1

    _DIMENSION_FIELDS: ClassVar[
        tuple[str, ...]
    ] = (
        "hypothesis_ids",
        "instruments",
        "timeframes",
        "data_periods",
        "indicator_configurations",
        "signal_rules",
        "execution_policies",
        "baselines",
    )

    def __post_init__(self) -> None:
        question_id = self._normalize_text(
            self.question_id,
            field_name="question_id",
        )
        validation_strategy = self._normalize_text(
            self.validation_strategy,
            field_name="validation_strategy",
        )
        evaluation_plan_ref = self._normalize_text(
            self.evaluation_plan_ref,
            field_name="evaluation_plan_ref",
        )

        object.__setattr__(
            self,
            "question_id",
            question_id,
        )
        object.__setattr__(
            self,
            "validation_strategy",
            validation_strategy,
        )
        object.__setattr__(
            self,
            "evaluation_plan_ref",
            evaluation_plan_ref,
        )

        for field_name in self._DIMENSION_FIELDS:
            normalized = self._normalize_text_items(
                getattr(self, field_name),
                field_name=field_name,
            )
            object.__setattr__(
                self,
                field_name,
                normalized,
            )

        object.__setattr__(
            self,
            "provenance",
            self._normalize_provenance(
                self.provenance
            ),
        )

    @property
    def id(self) -> str:
        return (
            "campaign-design:sha256:"
            f"{self.fingerprint}"
        )

    @property
    def fingerprint(self) -> str:
        serialized = json.dumps(
            self._identity_dict(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        )

        return sha256(
            serialized.encode("utf-8")
        ).hexdigest()

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.SCHEMA_VERSION,
            "id": self.id,
            "question_id": self.question_id,
            "hypothesis_ids": list(
                self.hypothesis_ids
            ),
            "instruments": list(
                self.instruments
            ),
            "timeframes": list(
                self.timeframes
            ),
            "data_periods": list(
                self.data_periods
            ),
            "indicator_configurations": list(
                self.indicator_configurations
            ),
            "signal_rules": list(
                self.signal_rules
            ),
            "execution_policies": list(
                self.execution_policies
            ),
            "baselines": list(
                self.baselines
            ),
            "validation_strategy": (
                self.validation_strategy
            ),
            "evaluation_plan_ref": (
                self.evaluation_plan_ref
            ),
            "provenance": {
                key: value
                for key, value in self.provenance
            },
        }

    def _identity_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.SCHEMA_VERSION,
            "question_id": self.question_id,
            "hypothesis_ids": list(
                self.hypothesis_ids
            ),
            "instruments": list(
                self.instruments
            ),
            "timeframes": list(
                self.timeframes
            ),
            "data_periods": list(
                self.data_periods
            ),
            "indicator_configurations": list(
                self.indicator_configurations
            ),
            "signal_rules": list(
                self.signal_rules
            ),
            "execution_policies": list(
                self.execution_policies
            ),
            "baselines": list(
                self.baselines
            ),
            "validation_strategy": (
                self.validation_strategy
            ),
            "evaluation_plan_ref": (
                self.evaluation_plan_ref
            ),
            "provenance": {
                key: value
                for key, value in self.provenance
            },
        }

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
        value: object,
        *,
        field_name: str,
    ) -> tuple[str, ...]:
        if not isinstance(value, tuple):
            raise TypeError(
                f"{field_name} must be a tuple"
            )

        if not value:
            raise ValueError(
                f"{field_name} must not be empty"
            )

        normalized = tuple(
            cls._normalize_text(
                item,
                field_name=field_name,
            )
            for item in value
        )

        if len(normalized) != len(set(normalized)):
            raise ValueError(
                f"{field_name} must not contain duplicates"
            )

        return tuple(sorted(normalized))

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

        return tuple(sorted(normalized))