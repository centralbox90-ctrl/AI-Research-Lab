from datetime import date, datetime
from typing import Any

from src.application.artifact_comparison import (
    ArtifactComparison,
)
from src.application.artifact_lineage import (
    ArtifactLineage,
)
from src.application.artifact_metadata import (
    ArtifactMetadata,
)
from src.application.market_experiment_specification import (
    MarketExperimentSpecification,
)
from src.application.research_cycle_serializer import (
    ResearchCycleSerializer,
)
from src.research import (
    NextExperimentResearchCycleResult,
    ResearchEnvironmentRef,
)


class ResearchArtifactSerializer:
    """
    Serializes a complete research execution artifact.

    The artifact combines:
    - optional artifact metadata;
    - optional artifact lineage;
    - optional artifact comparisons;
    - experiment specification;
    - research cycle.

    It does not depend on storage.
    """

    def __init__(
        self,
        cycle_serializer: (
            ResearchCycleSerializer | None
        ) = None,
    ) -> None:
        self.cycle_serializer = (
            cycle_serializer
            or ResearchCycleSerializer()
        )

    def serialize(
        self,
        specification: MarketExperimentSpecification,
        cycle: NextExperimentResearchCycleResult,
        metadata: ArtifactMetadata | None = None,
        lineage: ArtifactLineage | None = None,
        comparisons: list[ArtifactComparison] | None = None,
        research_environment: ResearchEnvironmentRef | None = None,
    ) -> dict[str, Any]:

        artifact = {
            "artifact_version": 1,
            "specification": (
                self._serialize_specification(
                    specification,
                )
            ),
            "cycle": self.cycle_serializer.serialize(
                cycle,
            ),
        }
        if research_environment is not None:
            artifact["research_environment"] = (
                self._serialize_research_environment(
                    research_environment,
                )
            )
        if metadata is not None:
            artifact["metadata"] = (
                self._serialize_metadata(
                    metadata,
                )
            )

        if lineage is not None:
            artifact["lineage"] = (
                self._serialize_lineage(
                    lineage,
                )
            )

        if comparisons is not None:
            artifact["comparisons"] = [
                self._serialize_comparison(
                    comparison,
                )
                for comparison in comparisons
            ]

        return artifact

    def _serialize_research_environment(
        self,
        environment: ResearchEnvironmentRef,
    ) -> dict[str, Any]:
        return {
            "dataset_fingerprint": (
                environment.dataset_fingerprint
            ),
            "assumption_set_fingerprint": (
                environment.assumption_set_fingerprint
            ),
            "code_version": environment.code_version,
            "executor_version": environment.executor_version,
            "statistical_method_version": (
                environment.statistical_method_version
            ),
            "random_seed": environment.random_seed,
            "fingerprint": environment.fingerprint(),
        }
    def _serialize_metadata(
        self,
        metadata: ArtifactMetadata,
    ) -> dict[str, Any]:
        return {
            "artifact_id": metadata.artifact_id,
            "schema_version": metadata.schema_version,
            "created_at": self._serialize_value(
                metadata.created_at,
            ),
            "experiment_id": metadata.experiment_id,
            "executor_type": metadata.executor_type,
            "executor_version": metadata.executor_version,
            "data_source": metadata.data_source,
            "code_version": metadata.code_version,
        }

    def _serialize_lineage(
        self,
        lineage: ArtifactLineage,
    ) -> dict[str, Any]:
        return {
            "parent_artifact_id": (
                lineage.parent_artifact_id
            ),
            "lineage_type": (
                lineage.lineage_type
            ),
            "change_description": (
                lineage.change_description
            ),
            "created_from_experiment": (
                lineage.created_from_experiment
            ),
        }

    def _serialize_comparison(
        self,
        comparison: ArtifactComparison,
    ) -> dict[str, Any]:
        return {
            "artifact_a_id": (
                comparison.artifact_a_id
            ),
            "artifact_b_id": (
                comparison.artifact_b_id
            ),
            "hypothesis_evolution": {
                "previous_hypothesis": (
                    comparison
                    .hypothesis_evolution
                    .previous_hypothesis
                ),
                "current_hypothesis": (
                    comparison
                    .hypothesis_evolution
                    .current_hypothesis
                ),
                "change_reason": (
                    comparison
                    .hypothesis_evolution
                    .change_reason
                ),
            },
            "evidence_evolution": {
                "previous_evidence": (
                    comparison
                    .evidence_evolution
                    .previous_evidence
                ),
                "current_evidence": (
                    comparison
                    .evidence_evolution
                    .current_evidence
                ),
                "metric_deltas": [
                    {
                        "metric_name": delta.metric_name,
                        "previous_value": (
                            delta.previous_value
                        ),
                        "current_value": (
                            delta.current_value
                        ),
                        "absolute_delta": (
                            delta.absolute_delta
                        ),
                        "direction": delta.direction,
                    }
                    for delta in (
                        comparison
                        .evidence_evolution
                        .metric_deltas
                    )
                ],
                "change_reason": (
                    comparison
                    .evidence_evolution
                    .change_reason
                ),
            },
            "confidence_evolution": {
                "previous_confidence": (
                    comparison
                    .confidence_evolution
                    .previous_confidence
                ),
                "current_confidence": (
                    comparison
                    .confidence_evolution
                    .current_confidence
                ),
                "change_reason": (
                    comparison
                    .confidence_evolution
                    .change_reason
                ),
            },
        }

    def _serialize_specification(
        self,
        specification: MarketExperimentSpecification,
    ) -> dict[str, Any]:
        return {
            "executor_type": specification.executor_type,
            "question_title": specification.question_title,
            "question_description": (
                specification.question_description
            ),
            "hypothesis_title": specification.hypothesis_title,
            "hypothesis_description": (
                specification.hypothesis_description
            ),
            "expected_result": specification.expected_result,
            "experiment_title": specification.experiment_title,
            "experiment_description": (
                specification.experiment_description
            ),
            "data_source": specification.data_source,
            "symbol": specification.symbol,
            "timeframe": specification.timeframe,
            "start_at": self._serialize_value(
                specification.start_at,
            ),
            "end_at": self._serialize_value(
                specification.end_at,
            ),
            "entry_rule": specification.entry_rule,
            "exit_rule": specification.exit_rule,
            "direction": specification.direction.value,
            "stop_loss_percent": (
                specification.stop_loss_percent
            ),
            "take_profit_percent": (
                specification.take_profit_percent
            ),
            "max_holding_bars": (
                specification.max_holding_bars
            ),
            "commission_percent": (
                specification.commission_percent
            ),
            "slippage_percent": (
                specification.slippage_percent
            ),
            "strategy_parameters": dict(
                specification.strategy_parameters,
            ),
            "tags": list(
                specification.tags,
            ),
        }

    def _serialize_value(
        self,
        value: Any,
    ) -> Any:
        if isinstance(value, (datetime, date)):
            return value.isoformat()

        return value