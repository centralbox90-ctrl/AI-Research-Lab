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

    The artifact contains:
    - artifact metadata;
    - optional artifact lineage;
    - original market experiment specification;
    - completed research cycle.

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
        lineage: ArtifactLineage | None = None,
        research_environment: ResearchEnvironmentRef | None = None,
    ) -> NextExperimentResearchCycleResult:
        """
        Execute research and persist a complete artifact.
        """

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
            executor_version=None,
            data_source=specification.data_source,
            code_version=None,
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