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
from src.research.research_campaign import ResearchCampaign

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

    def run_campaign(
        self,
        engine: ResearchEngine,
        question: Question,
        hypothesis: Hypothesis,
        campaign: ResearchCampaign,
        experiments: list[Experiment],
        executor: Callable[[Experiment], ExperimentResult],
    ) -> list[ResearchExecution]:
        """
        Runs a research campaign through the existing research engine.

        ResearchEngine remains responsible for campaign orchestration.
        AIScientist records the lifecycle of each individual cycle.
        """

        executions: list[ResearchExecution] = []
        active_execution: ResearchExecution | None = None

        def on_cycle_started(
            experiment: Experiment,
        ) -> None:
            nonlocal active_execution

            execution = ResearchExecution(
                question_id=question.id,
                hypothesis_id=hypothesis.id,
                experiment_id=experiment.id,
                status="RUNNING",
            )

            self.start_execution(execution)
            executions.append(execution)
            active_execution = execution

        def on_cycle_completed(
            experiment: Experiment,
            result: ResearchCycleResult,
        ) -> None:
            nonlocal active_execution

            if (
                active_execution is None
                or active_execution.experiment_id
                != experiment.id
            ):
                raise RuntimeError(
                    "completed cycle has no active execution"
                )

            active_execution.complete(result)
            active_execution.evidence_id = result.evidence.id
            active_execution.knowledge_id = result.knowledge.id

            active_execution = None

        try:
            engine.run_campaign(
                question=question,
                hypothesis=hypothesis,
                campaign=campaign,
                experiments=experiments,
                executor=executor,
                on_cycle_started=on_cycle_started,
                on_cycle_completed=on_cycle_completed,
            )

            return executions

        except Exception as error:
            if (
                active_execution is not None
                and not active_execution.is_completed()
            ):
                active_execution.fail(error)

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