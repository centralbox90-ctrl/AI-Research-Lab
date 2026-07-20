from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime

from src.research.cycle_results import ResearchCycleResult
from src.research.engine import ResearchEngine
from src.research.experiment import Experiment
from src.research.experiment_result import ExperimentResult
from src.research.hypothesis import Hypothesis
from src.research.question import Question
from src.research.research_execution import ResearchExecution


@dataclass
class AIScientist:
    """
    Coordinates research executions.
    """

    name: str = "AI Scientist"

    created_at: datetime = field(default_factory=datetime.now)

    executions: list[ResearchExecution] = field(default_factory=list)

    def start_execution(
        self,
        execution: ResearchExecution,
    ) -> None:
        self.executions.append(execution)

    def record_execution(
        self,
        execution: ResearchExecution,
    ) -> ResearchExecution:
        """
        Registers a completed research execution.
        """

        if execution in self.executions:
            return execution

        self.start_execution(execution)

        return execution

    def run_research(
        self,
        engine: ResearchEngine,
        question: Question,
        hypothesis: Hypothesis,
        experiment: Experiment,
        executor: Callable[[Experiment], ExperimentResult],
    ) -> ResearchExecution:
        """
        Runs one research cycle through the existing research engine.

        The method creates and registers exactly one ResearchExecution.
        Research computation remains the responsibility of ResearchEngine.
        """

        if (
            experiment.hypothesis_id
            and experiment.hypothesis_id != hypothesis.id
        ):
            raise ValueError(
                "experiment does not belong to hypothesis"
            )

        execution = ResearchExecution(
            question_id=question.id,
            hypothesis_id=hypothesis.id,
            experiment_id=experiment.id,
            status="RUNNING",
        )

        self.start_execution(execution)

        try:
            result: ResearchCycleResult = engine.run(
                question=question,
                hypothesis=hypothesis,
                experiment=experiment,
                executor=executor,
            )

            execution.complete(result)

            execution.evidence_id = result.evidence.id
            execution.knowledge_id = result.knowledge.id

            return execution

        except Exception as error:
            execution.fail(error)
            raise

    def completed_executions(self) -> list[ResearchExecution]:
        return [
            execution
            for execution in self.executions
            if execution.is_completed()
        ]

    def successful_executions(self) -> list[ResearchExecution]:
        return [
            execution
            for execution in self.executions
            if execution.success
        ]

    def total_executions(self) -> int:
        return len(self.executions)