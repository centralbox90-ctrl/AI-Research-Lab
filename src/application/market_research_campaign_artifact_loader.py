from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from src.application.research_artifact_envelope import (
    ResearchArtifactEnvelope,
    ResearchArtifactSourceReference,
    load_research_artifact_envelope,
)
from src.research.research_planner import (
    CampaignExperimentSpecification,
    ResearchCampaignPlan,
)


@dataclass(frozen=True, slots=True)
class LoadedMarketResearchCampaignExperimentArtifact:
    """One validated experiment entry from a Campaign envelope."""

    planned_specification: CampaignExperimentSpecification
    artifact: Mapping[str, object]
    result_id: str

    def __post_init__(self) -> None:
        if not isinstance(
            self.planned_specification,
            CampaignExperimentSpecification,
        ):
            raise TypeError(
                "planned_specification must be a "
                "CampaignExperimentSpecification"
            )

        if not isinstance(self.artifact, Mapping):
            raise TypeError(
                "artifact must be a mapping"
            )

        if not isinstance(self.result_id, str):
            raise TypeError(
                "result_id must be a string"
            )

        if not self.result_id.strip():
            raise ValueError(
                "result_id must not be empty"
            )


@dataclass(frozen=True, slots=True)
class LoadedMarketResearchCampaignArtifact:
    """Typed result of loading one Campaign envelope."""

    research_plan: ResearchCampaignPlan
    experiments: tuple[
        LoadedMarketResearchCampaignExperimentArtifact,
        ...,
    ]
    envelope: ResearchArtifactEnvelope

    def __post_init__(self) -> None:
        if not isinstance(
            self.research_plan,
            ResearchCampaignPlan,
        ):
            raise TypeError(
                "research_plan must be a "
                "ResearchCampaignPlan"
            )

        if not isinstance(self.experiments, tuple):
            raise TypeError(
                "experiments must be a tuple"
            )

        if any(
            not isinstance(
                experiment,
                LoadedMarketResearchCampaignExperimentArtifact,
            )
            for experiment in self.experiments
        ):
            raise TypeError(
                "experiments must contain "
                "LoadedMarketResearchCampaignExperimentArtifact "
                "values"
            )

        if not isinstance(
            self.envelope,
            ResearchArtifactEnvelope,
        ):
            raise TypeError(
                "envelope must be a "
                "ResearchArtifactEnvelope"
            )


class MarketResearchCampaignArtifactLoader:
    """Loads and validates one market-research Campaign envelope."""

    _PAYLOAD_FIELDS = {
        "campaign_design_id",
        "campaign_plan_id",
        "campaign_plan",
        "experiment_count",
        "experiments",
    }
    _PLAN_FIELDS = {
        "schema_version",
        "id",
        "campaign_design_id",
        "question_id",
        "experiment_specifications",
        "evaluation_plan_ref",
        "provenance",
    }
    _SPECIFICATION_FIELDS = {
        "schema_version",
        "id",
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
    }
    _EXPERIMENT_FIELDS = {
        "planned_experiment_id",
        "planned_specification",
        "artifact",
    }

    def load(
        self,
        serialized: Mapping[str, object],
    ) -> LoadedMarketResearchCampaignArtifact:
        if not isinstance(serialized, Mapping):
            raise TypeError(
                "serialized artifact must be a mapping"
            )

        envelope = load_research_artifact_envelope(
            serialized
        )

        if envelope.artifact_type != (
            "market_research_campaign"
        ):
            raise ValueError(
                "artifact_type must be "
                "market_research_campaign"
            )

        if envelope.payload_schema_version != 1:
            raise ValueError(
                "payload_schema_version must be 1"
            )

        payload = self._require_object(
            envelope.payload,
            label="payload",
        )
        self._validate_fields(
            payload,
            expected=self._PAYLOAD_FIELDS,
            label="payload",
        )

        research_plan = self._load_research_plan(
            payload["campaign_plan"]
        )

        if payload["campaign_design_id"] != (
            research_plan.campaign_design_id
        ):
            raise ValueError(
                "campaign_design_id does not match "
                "campaign_plan"
            )

        if payload["campaign_plan_id"] != (
            research_plan.id
        ):
            raise ValueError(
                "campaign_plan_id does not match "
                "campaign_plan"
            )

        experiment_count = payload[
            "experiment_count"
        ]

        if (
            not isinstance(experiment_count, int)
            or isinstance(experiment_count, bool)
            or experiment_count < 1
        ):
            raise ValueError(
                "experiment_count must be a "
                "positive integer"
            )

        experiment_payloads = self._require_array(
            payload["experiments"],
            label="experiments",
        )

        if experiment_count != len(
            experiment_payloads
        ):
            raise ValueError(
                "experiment_count does not match "
                "experiments"
            )

        if experiment_count != len(
            research_plan.experiment_specifications
        ):
            raise ValueError(
                "experiment_count does not match "
                "campaign_plan"
            )

        experiments = tuple(
            self._load_experiment(
                value,
                expected_specification=(
                    research_plan
                    .experiment_specifications[index]
                ),
                index=index,
            )
            for index, value
            in enumerate(experiment_payloads)
        )

        self._validate_provenance(
            envelope=envelope,
            research_plan=research_plan,
            experiment_count=experiment_count,
        )
        self._validate_source_references(
            envelope=envelope,
            research_plan=research_plan,
            experiments=experiments,
        )

        return LoadedMarketResearchCampaignArtifact(
            research_plan=research_plan,
            experiments=experiments,
            envelope=envelope,
        )

    def _load_research_plan(
        self,
        value: object,
    ) -> ResearchCampaignPlan:
        serialized = self._require_object(
            value,
            label="campaign_plan",
        )
        self._validate_fields(
            serialized,
            expected=self._PLAN_FIELDS,
            label="campaign_plan",
        )

        if serialized["schema_version"] != 1:
            raise ValueError(
                "campaign_plan.schema_version "
                "must be 1"
            )

        specification_payloads = (
            self._require_array(
                serialized[
                    "experiment_specifications"
                ],
                label=(
                    "campaign_plan."
                    "experiment_specifications"
                ),
            )
        )
        specifications = tuple(
            self._load_specification(
                item,
                label=(
                    "campaign_plan."
                    "experiment_specifications"
                    f"[{index}]"
                ),
            )
            for index, item
            in enumerate(specification_payloads)
        )
        provenance_payload = (
            self._require_object(
                serialized["provenance"],
                label="campaign_plan.provenance",
            )
        )
        provenance: list[tuple[str, str]] = []

        for key, item in provenance_payload.items():
            provenance.append(
                (
                    self._require_text(
                        key,
                        label=(
                            "campaign_plan."
                            "provenance key"
                        ),
                    ),
                    self._require_text(
                        item,
                        label=(
                            "campaign_plan."
                            f"provenance.{key}"
                        ),
                    ),
                )
            )

        try:
            plan = ResearchCampaignPlan(
                campaign_design_id=serialized[
                    "campaign_design_id"
                ],
                question_id=serialized["question_id"],
                experiment_specifications=(
                    specifications
                ),
                evaluation_plan_ref=serialized[
                    "evaluation_plan_ref"
                ],
                provenance=tuple(provenance),
            )
        except (TypeError, ValueError) as error:
            raise ValueError(
                f"campaign_plan is invalid: {error}"
            ) from error

        if serialized["id"] != plan.id:
            raise ValueError(
                "campaign_plan.id does not match "
                "campaign_plan fingerprint"
            )

        if self._thaw(serialized) != plan.to_dict():
            raise ValueError(
                "campaign_plan is not canonical"
            )

        return plan

    def _load_specification(
        self,
        value: object,
        *,
        label: str,
    ) -> CampaignExperimentSpecification:
        serialized = self._require_object(
            value,
            label=label,
        )
        self._validate_fields(
            serialized,
            expected=self._SPECIFICATION_FIELDS,
            label=label,
        )

        if serialized["schema_version"] != 1:
            raise ValueError(
                f"{label}.schema_version must be 1"
            )

        try:
            specification = (
                CampaignExperimentSpecification(
                    campaign_design_id=serialized[
                        "campaign_design_id"
                    ],
                    question_id=serialized[
                        "question_id"
                    ],
                    hypothesis_id=serialized[
                        "hypothesis_id"
                    ],
                    instrument=serialized[
                        "instrument"
                    ],
                    timeframe=serialized[
                        "timeframe"
                    ],
                    data_period=serialized[
                        "data_period"
                    ],
                    indicator_configuration=(
                        serialized[
                            "indicator_configuration"
                        ]
                    ),
                    signal_rule=serialized[
                        "signal_rule"
                    ],
                    execution_policy=serialized[
                        "execution_policy"
                    ],
                    baseline=serialized["baseline"],
                    validation_strategy=serialized[
                        "validation_strategy"
                    ],
                    evaluation_plan_ref=serialized[
                        "evaluation_plan_ref"
                    ],
                )
            )
        except (TypeError, ValueError) as error:
            raise ValueError(
                f"{label} is invalid: {error}"
            ) from error

        if serialized["id"] != specification.id:
            raise ValueError(
                f"{label}.id does not match "
                "specification fingerprint"
            )

        if (
            self._thaw(serialized)
            != specification.to_dict()
        ):
            raise ValueError(
                f"{label} is not canonical"
            )

        return specification

    def _load_experiment(
        self,
        value: object,
        *,
        expected_specification: (
            CampaignExperimentSpecification
        ),
        index: int,
    ) -> LoadedMarketResearchCampaignExperimentArtifact:
        label = f"experiments[{index}]"
        serialized = self._require_object(
            value,
            label=label,
        )
        self._validate_fields(
            serialized,
            expected=self._EXPERIMENT_FIELDS,
            label=label,
        )
        planned_experiment_id = (
            self._require_text(
                serialized[
                    "planned_experiment_id"
                ],
                label=(
                    f"{label}."
                    "planned_experiment_id"
                ),
            )
        )
        planned_specification = (
            self._load_specification(
                serialized[
                    "planned_specification"
                ],
                label=(
                    f"{label}."
                    "planned_specification"
                ),
            )
        )

        if planned_experiment_id != (
            expected_specification.id
        ):
            raise ValueError(
                f"{label}.planned_experiment_id "
                "does not match campaign_plan order"
            )

        if planned_specification != (
            expected_specification
        ):
            raise ValueError(
                f"{label}.planned_specification "
                "does not match campaign_plan"
            )

        artifact = self._require_object(
            serialized["artifact"],
            label=f"{label}.artifact",
        )

        if artifact.get("artifact_version") != 1:
            raise ValueError(
                f"{label}.artifact.artifact_version "
                "must be 1"
            )

        self._require_object(
            artifact.get("specification"),
            label=f"{label}.artifact.specification",
        )
        cycle = self._require_object(
            artifact.get("cycle"),
            label=f"{label}.artifact.cycle",
        )
        result = self._require_object(
            cycle.get("result"),
            label=f"{label}.artifact.cycle.result",
        )
        result_id = self._require_text(
            result.get("id"),
            label=(
                f"{label}."
                "artifact.cycle.result.id"
            ),
        )

        return (
            LoadedMarketResearchCampaignExperimentArtifact(
                planned_specification=(
                    planned_specification
                ),
                artifact=artifact,
                result_id=result_id,
            )
        )

    @staticmethod
    def _validate_provenance(
        *,
        envelope: ResearchArtifactEnvelope,
        research_plan: ResearchCampaignPlan,
        experiment_count: int,
    ) -> None:
        expected: dict[str, object] = dict(
            research_plan.provenance
        )
        expected.update(
            {
                "campaign_design_id": (
                    research_plan.campaign_design_id
                ),
                "campaign_plan_fingerprint": (
                    research_plan.fingerprint
                ),
                "campaign_plan_id": (
                    research_plan.id
                ),
                "experiment_count": (
                    experiment_count
                ),
                "question_id": (
                    research_plan.question_id
                ),
            }
        )

        if dict(envelope.provenance) != expected:
            raise ValueError(
                "provenance does not match "
                "campaign_plan"
            )

    @staticmethod
    def _validate_source_references(
        *,
        envelope: ResearchArtifactEnvelope,
        research_plan: ResearchCampaignPlan,
        experiments: tuple[
            LoadedMarketResearchCampaignExperimentArtifact,
            ...,
        ],
    ) -> None:
        expected = (
            ResearchArtifactSourceReference(
                reference_type=(
                    "research_campaign_plan"
                ),
                reference_id=research_plan.id,
                reference_fingerprint=(
                    research_plan.fingerprint
                ),
            ),
            *(
                ResearchArtifactSourceReference(
                    reference_type=(
                        "experiment_result"
                    ),
                    reference_id=(
                        experiment.result_id
                    ),
                )
                for experiment in experiments
            ),
        )

        if envelope.source_references != expected:
            raise ValueError(
                "source_references do not match "
                "campaign payload"
            )

    @staticmethod
    def _require_object(
        value: object,
        *,
        label: str,
    ) -> Mapping[str, object]:
        if not isinstance(value, Mapping):
            raise ValueError(
                f"{label} must be an object"
            )

        if any(
            not isinstance(key, str)
            for key in value
        ):
            raise ValueError(
                f"{label} field names must be strings"
            )

        return value

    @staticmethod
    def _require_array(
        value: object,
        *,
        label: str,
    ) -> tuple[object, ...]:
        if not isinstance(value, (list, tuple)):
            raise ValueError(
                f"{label} must be an array"
            )

        return tuple(value)

    @staticmethod
    def _require_text(
        value: object,
        *,
        label: str,
    ) -> str:
        if not isinstance(value, str):
            raise ValueError(
                f"{label} must be a string"
            )

        normalized = value.strip()

        if not normalized:
            raise ValueError(
                f"{label} must not be empty"
            )

        if normalized != value:
            raise ValueError(
                f"{label} must be normalized"
            )

        return normalized

    @staticmethod
    def _validate_fields(
        payload: Mapping[str, object],
        *,
        expected: set[str],
        label: str,
    ) -> None:
        fields = set(payload)
        missing = sorted(expected - fields)
        unknown = sorted(fields - expected)

        if missing:
            raise ValueError(
                f"{label} missing fields: "
                + ", ".join(missing)
            )

        if unknown:
            raise ValueError(
                f"{label} unknown fields: "
                + ", ".join(unknown)
            )

    @classmethod
    def _thaw(
        cls,
        value: object,
    ) -> Any:
        if isinstance(value, Mapping):
            return {
                key: cls._thaw(item)
                for key, item in value.items()
            }

        if isinstance(value, tuple):
            return [
                cls._thaw(item)
                for item in value
            ]

        return value
