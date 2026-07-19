from typing import Any

from src.application.artifact_lineage import (
    ArtifactLineage,
)
from src.application.get_stored_research_artifact import (
    GetStoredResearchArtifact,
)
from src.application.market_experiment_specification import (
    MarketExperimentSpecification,
)
from src.application.next_experiment_factory import (
    NextExperimentFactory,
)
from src.application.run_and_store_research_artifact import (
    RunAndStoreResearchArtifact,
)
from src.research import (
    Experiment,
    Hypothesis,
    NextExperimentResearchCycleResult,
    NextExperimentSelection,
    Question,
    ResearchEnvironmentRef,
)


class RunSelectedNextExperiment:
    """
    Executes a selected next research action as a child artifact.
    """

    def __init__(
        self,
        artifact_getter: GetStoredResearchArtifact,
        artifact_runner: RunAndStoreResearchArtifact,
        next_experiment_factory: (
            NextExperimentFactory | None
        ) = None,
    ) -> None:
        self.artifact_getter = artifact_getter
        self.artifact_runner = artifact_runner
        self.next_experiment_factory = (
            next_experiment_factory
            or NextExperimentFactory()
        )

    def execute(
        self,
        parent_result_id: str,
        specification: MarketExperimentSpecification,
        question: Question,
        hypothesis: Hypothesis,
        parent_experiment: Experiment,
        selection: NextExperimentSelection,
        research_environment: ResearchEnvironmentRef,
        executor: Any,
    ) -> NextExperimentResearchCycleResult:
        parent_artifact = self.artifact_getter.execute(
            parent_result_id,
        )

        if parent_artifact is None:
            raise ValueError(
                "Research artifact was not found for result_id: "
                f"{parent_result_id}"
            )

        parent_artifact_id = self._extract_artifact_id(
            parent_artifact,
        )

        child_experiment = self.next_experiment_factory.create(
            parent_experiment=parent_experiment,
            selection=selection,
        )

        lineage = ArtifactLineage(
            parent_artifact_id=parent_artifact_id,
            lineage_type="derived_from",
            change_description=(
                "Executed selected next research action: "
                f"{selection.action}."
            ),
            created_from_experiment=child_experiment.id,
        )

        return self.artifact_runner.execute(
            specification=specification,
            question=question,
            hypothesis=hypothesis,
            experiment=child_experiment,
            executor=executor,
            research_environment=research_environment,
            lineage=lineage,
        )

    def _extract_artifact_id(
        self,
        artifact: dict[str, Any],
    ) -> str:
        metadata = artifact.get("metadata")

        if not isinstance(metadata, dict):
            raise ValueError(
                "Parent research artifact must contain metadata."
            )

        artifact_id = metadata.get("artifact_id")

        if not isinstance(artifact_id, str) or not artifact_id:
            raise ValueError(
                "Parent research artifact metadata must contain "
                "artifact_id."
            )

        return artifact_id