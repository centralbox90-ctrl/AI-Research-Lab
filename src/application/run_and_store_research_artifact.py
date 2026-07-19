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
    ) -> None:
        self.store = store

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

        self.store.save(
            result_id=cycle.result.id,
            serialized_cycle=artifact,
        )

        return cycle