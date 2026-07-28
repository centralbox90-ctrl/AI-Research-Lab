from typing import Any

from src.application.artifact_lineage import (
    ArtifactLineage,
)
from src.application.artifact_metadata_factory import (
    ArtifactMetadataFactory,
)
from src.application.market_experiment_specification import (
    MarketExperimentSpecification,
)
from src.application.research_artifact_envelope import (
    ResearchArtifactEnvelopeFactory,
    ResearchArtifactSourceReference,
)
from src.application.research_artifact_serializer import (
    ResearchArtifactSerializer,
)
from src.application.serialized_research_cycle_store import (
    SerializedResearchCycleStore,
)
from src.research import (
    Experiment,
    Hypothesis,
    NextExperimentResearchCycleResult,
    Question,
    ResearchEngine,
    ResearchEnvironmentRef,
)
from src.research.experiment_execution import (
    ExperimentExecution,
    ExperimentExecutionStatus,
)


class RunAndStoreResearchArtifact:
    """
    Runs a research cycle and stores a reproducible research artifact.

    Every persisted artifact must include the immutable research
    environment that identifies the dataset, assumptions, code,
    executor, statistical method, and random seed used by the run.

    This use case keeps artifact persistence outside the research
    domain and outside storage implementation details.
    """

    def __init__(
        self,
        store: SerializedResearchCycleStore,
        research_engine: ResearchEngine | None = None,
        serializer: ResearchArtifactSerializer | None = None,
        metadata_factory: ArtifactMetadataFactory | None = None,
        envelope_factory: (
            ResearchArtifactEnvelopeFactory | None
        ) = None,
    ) -> None:
        self.store = store
        self.envelope_factory = envelope_factory

        self.research_engine = (
            research_engine
            or ResearchEngine()
        )

        self.serializer = (
            serializer
            or ResearchArtifactSerializer()
        )

        self.metadata_factory = (
            metadata_factory
            or ArtifactMetadataFactory()
        )

    def execute(
        self,
        specification: MarketExperimentSpecification,
        question: Question,
        hypothesis: Hypothesis,
        experiment: Experiment,
        executor: Any,
        research_environment: ResearchEnvironmentRef,
        lineage: ArtifactLineage | None = None,
    ) -> NextExperimentResearchCycleResult:
        """
        Execute research and persist a reproducible artifact.
        """

        if not isinstance(
            research_environment,
            ResearchEnvironmentRef,
        ):
            raise TypeError(
                "research_environment must be a "
                "ResearchEnvironmentRef"
            )

        cycle = (
            self.research_engine.run_with_next_experiment_selection(
                question=question,
                hypothesis=hypothesis,
                experiment=experiment,
                executor=executor,
            )
        )

        metadata = self.metadata_factory.create(
            experiment_id=str(experiment.id),
            executor_type=specification.executor_type,
            executor_version=(
                research_environment.executor_version
            ),
            data_source=specification.data_source,
            code_version=(
                research_environment.code_version
            ),
        )

        artifact = self.serializer.serialize(
            specification=specification,
            cycle=cycle,
            metadata=metadata,
            lineage=lineage,
            research_environment=research_environment,
        )

        serialized_artifact = artifact

        if self.envelope_factory is not None:
            execution = getattr(
                executor,
                "execution",
                None,
            )

            if not isinstance(
                execution,
                ExperimentExecution,
            ):
                raise TypeError(
                    "envelope production requires "
                    "an executor exposing "
                    "ExperimentExecution"
                )

            if (
                execution.status
                is not
                ExperimentExecutionStatus.SUCCEEDED
            ):
                raise ValueError(
                    "envelope production requires "
                    "a SUCCEEDED execution"
                )

            if execution.result_id != cycle.result.id:
                raise ValueError(
                    "execution result_id does not match "
                    "research cycle result"
                )

            payload_schema_version = artifact.get(
                "artifact_version"
            )

            if (
                not isinstance(
                    payload_schema_version,
                    int,
                )
                or isinstance(
                    payload_schema_version,
                    bool,
                )
                or payload_schema_version <= 0
            ):
                raise ValueError(
                    "serialized artifact must contain "
                    "a positive artifact_version"
                )

            serialized_artifact = (
                self.envelope_factory.create(
                    artifact_type=(
                        "market_research_cycle"
                    ),
                    payload_schema_version=(
                        payload_schema_version
                    ),
                    correlation_id=(
                        execution.correlation_id
                    ),
                    source_references=(
                        ResearchArtifactSourceReference(
                            reference_type=(
                                "experiment_execution"
                            ),
                            reference_id=(
                                execution.execution_id
                            ),
                        ),
                        ResearchArtifactSourceReference(
                            reference_type=(
                                "experiment_result"
                            ),
                            reference_id=cycle.result.id,
                        ),
                    ),
                    provenance={
                        "specification_fingerprint": (
                            specification.fingerprint
                        ),
                        "environment_fingerprint": (
                            research_environment
                            .fingerprint()
                        ),
                        "dataset_fingerprint": (
                            research_environment
                            .dataset_fingerprint
                        ),
                        "assumption_set_fingerprint": (
                            research_environment
                            .assumption_set_fingerprint
                        ),
                        "code_version": (
                            research_environment
                            .code_version
                        ),
                        "executor_version": (
                            research_environment
                            .executor_version
                        ),
                        "statistical_method_version": (
                            research_environment
                            .statistical_method_version
                        ),
                        "random_seed": (
                            research_environment
                            .random_seed
                        ),
                    },
                    payload=artifact,
                ).to_dict()
            )

        self.store.save(
            result_id=cycle.result.id,
            serialized_cycle=serialized_artifact,
        )

        return cycle