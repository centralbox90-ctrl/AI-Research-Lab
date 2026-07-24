from __future__ import annotations

import json
from dataclasses import dataclass
from hashlib import sha256
from itertools import product
from math import prod
from typing import ClassVar

from src.research.campaign_design import (
    CampaignDesign,
)


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


def _fingerprint(
    payload: dict[str, object],
) -> str:
    serialized = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )

    return sha256(
        serialized.encode("utf-8")
    ).hexdigest()


@dataclass(frozen=True, slots=True)
class CampaignExperimentSpecification:
    """
    One immutable experiment selected from CampaignDesign.
    """

    campaign_design_id: str
    question_id: str
    hypothesis_id: str
    instrument: str
    timeframe: str
    data_period: str
    indicator_configuration: str
    signal_rule: str
    execution_policy: str
    baseline: str
    validation_strategy: str
    evaluation_plan_ref: str

    SCHEMA_VERSION: ClassVar[int] = 1

    def __post_init__(self) -> None:
        for field_name in (
            "campaign_design_id",
            "question_id",
            "hypothesis_id",
            "instrument",
            "timeframe",
            "data_period",
            "indicator_configuration",
            "signal_rule",
            "execution_policy",
            "baseline",
            "validation_strategy",
            "evaluation_plan_ref",
        ):
            object.__setattr__(
                self,
                field_name,
                _normalize_text(
                    getattr(self, field_name),
                    field_name=field_name,
                ),
            )

    @property
    def id(self) -> str:
        return (
            "campaign-experiment-specification:"
            f"sha256:{self.fingerprint}"
        )

    @property
    def fingerprint(self) -> str:
        return _fingerprint(
            self._identity_dict()
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.SCHEMA_VERSION,
            "id": self.id,
            **self._identity_dict(),
        }

    def _identity_dict(self) -> dict[str, object]:
        return {
            "campaign_design_id": (
                self.campaign_design_id
            ),
            "question_id": self.question_id,
            "hypothesis_id": self.hypothesis_id,
            "instrument": self.instrument,
            "timeframe": self.timeframe,
            "data_period": self.data_period,
            "indicator_configuration": (
                self.indicator_configuration
            ),
            "signal_rule": self.signal_rule,
            "execution_policy": (
                self.execution_policy
            ),
            "baseline": self.baseline,
            "validation_strategy": (
                self.validation_strategy
            ),
            "evaluation_plan_ref": (
                self.evaluation_plan_ref
            ),
        }


@dataclass(frozen=True, slots=True)
class ResearchCampaignPlan:
    """
    Reproducible planned campaign produced before execution.
    """

    campaign_design_id: str
    question_id: str
    experiment_specifications: tuple[
        CampaignExperimentSpecification,
        ...,
    ]
    evaluation_plan_ref: str
    provenance: tuple[
        tuple[str, str],
        ...,
    ]

    SCHEMA_VERSION: ClassVar[int] = 1

    def __post_init__(self) -> None:
        campaign_design_id = _normalize_text(
            self.campaign_design_id,
            field_name="campaign_design_id",
        )
        question_id = _normalize_text(
            self.question_id,
            field_name="question_id",
        )
        evaluation_plan_ref = _normalize_text(
            self.evaluation_plan_ref,
            field_name="evaluation_plan_ref",
        )

        if not isinstance(
            self.experiment_specifications,
            tuple,
        ):
            raise TypeError(
                "experiment_specifications must be a tuple"
            )

        if not self.experiment_specifications:
            raise ValueError(
                "experiment_specifications "
                "must not be empty"
            )

        if any(
            not isinstance(
                specification,
                CampaignExperimentSpecification,
            )
            for specification
            in self.experiment_specifications
        ):
            raise TypeError(
                "each experiment specification must be a "
                "CampaignExperimentSpecification"
            )

        for specification in (
            self.experiment_specifications
        ):
            if (
                specification.campaign_design_id
                != campaign_design_id
            ):
                raise ValueError(
                    "experiment specification campaign "
                    "design must match the plan"
                )

            if specification.question_id != question_id:
                raise ValueError(
                    "experiment specification question "
                    "must match the plan"
                )

            if (
                specification.evaluation_plan_ref
                != evaluation_plan_ref
            ):
                raise ValueError(
                    "experiment specification evaluation "
                    "plan must match the campaign plan"
                )

        normalized_specifications = tuple(
            sorted(
                self.experiment_specifications,
                key=lambda specification: (
                    specification.id
                ),
            )
        )
        specification_ids = tuple(
            specification.id
            for specification
            in normalized_specifications
        )

        if len(specification_ids) != len(
            set(specification_ids)
        ):
            raise ValueError(
                "experiment specification IDs "
                "must be unique"
            )

        provenance = self._normalize_provenance(
            self.provenance
        )

        object.__setattr__(
            self,
            "campaign_design_id",
            campaign_design_id,
        )
        object.__setattr__(
            self,
            "question_id",
            question_id,
        )
        object.__setattr__(
            self,
            "evaluation_plan_ref",
            evaluation_plan_ref,
        )
        object.__setattr__(
            self,
            "experiment_specifications",
            normalized_specifications,
        )
        object.__setattr__(
            self,
            "provenance",
            provenance,
        )

    @property
    def id(self) -> str:
        return (
            "research-campaign-plan:"
            f"sha256:{self.fingerprint}"
        )

    @property
    def fingerprint(self) -> str:
        return _fingerprint(
            self._identity_dict()
        )

    @property
    def experiment_ids(self) -> tuple[str, ...]:
        return tuple(
            specification.id
            for specification
            in self.experiment_specifications
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.SCHEMA_VERSION,
            "id": self.id,
            **self._identity_dict(),
        }

    def _identity_dict(self) -> dict[str, object]:
        return {
            "campaign_design_id": (
                self.campaign_design_id
            ),
            "question_id": self.question_id,
            "experiment_specifications": [
                specification.to_dict()
                for specification
                in self.experiment_specifications
            ],
            "evaluation_plan_ref": (
                self.evaluation_plan_ref
            ),
            "provenance": {
                key: value
                for key, value in self.provenance
            },
        }

    @staticmethod
    def _normalize_provenance(
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

            key = _normalize_text(
                entry[0],
                field_name="provenance key",
            )
            item = _normalize_text(
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


class ResearchPlanner:
    """
    Expands CampaignDesign into a deterministic Cartesian plan.
    """

    DEFAULT_VERSION = "research-planner-v1"
    DEFAULT_MAXIMUM_EXPERIMENT_COUNT = 10_000

    def __init__(
        self,
        *,
        version: str = DEFAULT_VERSION,
        maximum_experiment_count: int = (
            DEFAULT_MAXIMUM_EXPERIMENT_COUNT
        ),
    ) -> None:
        self._version = _normalize_text(
            version,
            field_name="version",
        )

        if (
            not isinstance(
                maximum_experiment_count,
                int,
            )
            or isinstance(
                maximum_experiment_count,
                bool,
            )
        ):
            raise TypeError(
                "maximum_experiment_count "
                "must be an integer"
            )

        if maximum_experiment_count < 1:
            raise ValueError(
                "maximum_experiment_count "
                "must be positive"
            )

        self._maximum_experiment_count = (
            maximum_experiment_count
        )

    @property
    def version(self) -> str:
        return self._version

    @property
    def maximum_experiment_count(self) -> int:
        return self._maximum_experiment_count

    def plan(
        self,
        design: CampaignDesign,
    ) -> ResearchCampaignPlan:
        if not isinstance(design, CampaignDesign):
            raise TypeError(
                "design must be a CampaignDesign"
            )

        experiment_count = prod(
            (
                len(design.hypothesis_ids),
                len(design.instruments),
                len(design.timeframes),
                len(design.data_periods),
                len(
                    design.indicator_configurations
                ),
                len(design.signal_rules),
                len(design.execution_policies),
                len(design.baselines),
            )
        )

        if (
            experiment_count
            > self._maximum_experiment_count
        ):
            raise ValueError(
                "campaign design expands to "
                f"{experiment_count} experiments, "
                "exceeding maximum_experiment_count "
                f"{self._maximum_experiment_count}"
            )

        specifications = tuple(
            CampaignExperimentSpecification(
                campaign_design_id=design.id,
                question_id=design.question_id,
                hypothesis_id=hypothesis_id,
                instrument=instrument,
                timeframe=timeframe,
                data_period=data_period,
                indicator_configuration=(
                    indicator_configuration
                ),
                signal_rule=signal_rule,
                execution_policy=execution_policy,
                baseline=baseline,
                validation_strategy=(
                    design.validation_strategy
                ),
                evaluation_plan_ref=(
                    design.evaluation_plan_ref
                ),
            )
            for (
                hypothesis_id,
                instrument,
                timeframe,
                data_period,
                indicator_configuration,
                signal_rule,
                execution_policy,
                baseline,
            ) in product(
                design.hypothesis_ids,
                design.instruments,
                design.timeframes,
                design.data_periods,
                design.indicator_configurations,
                design.signal_rules,
                design.execution_policies,
                design.baselines,
            )
        )

        return ResearchCampaignPlan(
            campaign_design_id=design.id,
            question_id=design.question_id,
            experiment_specifications=(
                specifications
            ),
            evaluation_plan_ref=(
                design.evaluation_plan_ref
            ),
            provenance=(
                (
                    "campaign_design_fingerprint",
                    design.fingerprint,
                ),
                (
                    "planner_version",
                    self._version,
                ),
            ),
        )