from collections.abc import Callable

from src.research.analysis import Analysis
from src.research.conclusion import Conclusion
from src.research.contradiction_evaluation import (
    ContradictionEvaluation,
)
from src.research.contradiction_evaluator import ContradictionEvaluator
from src.research.cycle_results import (
    ContradictionEvaluatedResearchCycleResult,
    DecidedResearchCycleResult,
    EvaluatedResearchCycleResult,
    EvidenceStrengthResearchCycleResult,
    NextExperimentResearchCycleResult,
    ResearchCycleResult,
    RobustnessEvaluatedResearchCycleResult,
    StatisticallyEvaluatedResearchCycleResult,
)
from src.research.evidence_strength_evaluation import (
    EvidenceStrengthEvaluation,
)
from src.research.evidence_strength_evaluator import (
    EvidenceStrengthEvaluator,
)
from src.research.evidence_strength_ranker import EvidenceStrengthRanker
from src.research.experiment import Experiment
from src.research.research_campaign import (
    ResearchCampaign,
)
from src.research.experiment_comparator import (
    ExperimentComparator,
    RankedExperiment,
)
from src.research.experiment_evaluation import ExperimentEvaluation
from src.research.experiment_evaluator import ExperimentEvaluator
from src.research.experiment_result import ExperimentResult
from src.research.experiment_runner import ExperimentRunner
from src.research.hypothesis import Hypothesis
from src.research.hypothesis_decision import HypothesisDecision
from src.research.hypothesis_decision_evaluator import (
    HypothesisDecisionEvaluator,
)
from src.research.knowledge import Knowledge
from src.research.next_experiment_selection import (
    NextExperimentSelection,
)
from src.research.next_experiment_selector import NextExperimentSelector
from src.research.question import Question
from src.research.research_objects_builder import ResearchObjectsBuilder
from src.research.ranked_evidence import RankedEvidence
from src.research.robustness_evaluation import RobustnessEvaluation
from src.research.robustness_evaluator import RobustnessEvaluator
from src.research.statistical_evaluation import StatisticalEvaluation
from src.research.statistical_evaluator import StatisticalEvaluator


class ResearchEngine:
    """
    РљРѕРѕСЂРґРёРЅРёСЂСѓРµС‚ РІС‹РїРѕР»РЅРµРЅРёРµ РёСЃСЃР»РµРґРѕРІР°С‚РµР»СЊСЃРєРёС… С†РёРєР»РѕРІ.
    """

    def __init__(self) -> None:
        self.runner = ExperimentRunner()
        self.evaluator = ExperimentEvaluator()
        self.statistical_evaluator = StatisticalEvaluator()
        self.robustness_evaluator = RobustnessEvaluator()
        self.contradiction_evaluator = ContradictionEvaluator()
        self.evidence_strength_evaluator = EvidenceStrengthEvaluator()
        self.evidence_strength_ranker = EvidenceStrengthRanker()
        self.hypothesis_decision_evaluator = (
            HypothesisDecisionEvaluator()
        )
        self.next_experiment_selector = NextExperimentSelector()
        self.comparator = ExperimentComparator()
        self.research_objects_builder = ResearchObjectsBuilder()

    def run(
        self,
        question: Question,
        hypothesis: Hypothesis,
        experiment: Experiment,
        executor: Callable[[Experiment], ExperimentResult],
    ) -> ResearchCycleResult:
        result = self.runner.run(experiment, executor)

        evidence, analysis, conclusion, knowledge = (
            self.research_objects_builder.build(
                question=question,
                hypothesis=hypothesis,
                experiment=experiment,
                result=result,
            )
        )

        return ResearchCycleResult(
            result=result,
            evidence=evidence,
            analysis=analysis,
            conclusion=conclusion,
            knowledge=knowledge,
        )
    def run_campaign(
        self,
        question: Question,
        hypothesis: Hypothesis,
        campaign: ResearchCampaign,
        experiments: list[Experiment],
        executor: Callable[
            [Experiment],
            ExperimentResult,
        ],
        on_cycle_started: Callable[
            [Experiment],
            None,
        ] | None = None,
        on_cycle_completed: Callable[
            [Experiment, ResearchCycleResult],
            None,
        ] | None = None,
    ) -> list[ResearchCycleResult]:
        if campaign.hypothesis_id != hypothesis.id:
            raise ValueError(
                "campaign does not belong to hypothesis"
            )

        experiment_ids = {
            experiment.id
            for experiment in experiments
        }

        if not experiment_ids.issubset(
            set(campaign.experiment_ids)
        ):
            raise ValueError(
                "campaign does not contain all experiments"
            )

        campaign.start()

        results: list[ResearchCycleResult] = []

        try:
            for experiment in experiments:
                if on_cycle_started is not None:
                    on_cycle_started(experiment)

                result = self.run(
                    question=question,
                    hypothesis=hypothesis,
                    experiment=experiment,
                    executor=executor,
                )

                results.append(result)

                if on_cycle_completed is not None:
                    on_cycle_completed(
                        experiment,
                        result,
                    )

            campaign.complete()

            return results

        except Exception:
            campaign.fail()
            raise
    def run_with_evaluation(
        self,
        question: Question,
        hypothesis: Hypothesis,
        experiment: Experiment,
        executor: Callable[[Experiment], ExperimentResult],
    ) -> EvaluatedResearchCycleResult:
        result = self.runner.run(experiment, executor)
        evaluation = self.evaluator.evaluate(result)

        evidence, analysis, conclusion, knowledge = (
            self.research_objects_builder.build(
                question=question,
                hypothesis=hypothesis,
                experiment=experiment,
                result=result,
                evaluation=evaluation,
            )
        )

        return EvaluatedResearchCycleResult(
            result=result,
            evaluation=evaluation,
            evidence=evidence,
            analysis=analysis,
            conclusion=conclusion,
            knowledge=knowledge,
        )

    def run_with_statistical_evaluation(
        self,
        question: Question,
        hypothesis: Hypothesis,
        experiment: Experiment,
        executor: Callable[[Experiment], ExperimentResult],
    ) -> StatisticallyEvaluatedResearchCycleResult:
        result = self.runner.run(experiment, executor)
        evaluation = self.evaluator.evaluate(result)

        statistical_evaluation = self.statistical_evaluator.evaluate(
            result
        )

        evidence, analysis, conclusion, knowledge = (
            self.research_objects_builder.build(
                question=question,
                hypothesis=hypothesis,
                experiment=experiment,
                result=result,
                evaluation=evaluation,
                statistical_evaluation=statistical_evaluation,
            )
        )

        return StatisticallyEvaluatedResearchCycleResult(
            result=result,
            evaluation=evaluation,
            statistical_evaluation=statistical_evaluation,
            evidence=evidence,
            analysis=analysis,
            conclusion=conclusion,
            knowledge=knowledge,
        )

    def run_with_robustness_evaluation(
        self,
        question: Question,
        hypothesis: Hypothesis,
        experiment: Experiment,
        executor: Callable[[Experiment], ExperimentResult],
    ) -> RobustnessEvaluatedResearchCycleResult:
        result = self.runner.run(experiment, executor)
        evaluation = self.evaluator.evaluate(result)

        statistical_evaluation = self.statistical_evaluator.evaluate(
            result
        )

        robustness_evaluation = self.robustness_evaluator.evaluate(
            result
        )

        evidence, analysis, conclusion, knowledge = (
            self.research_objects_builder.build(
                question=question,
                hypothesis=hypothesis,
                experiment=experiment,
                result=result,
                evaluation=evaluation,
                statistical_evaluation=statistical_evaluation,
                robustness_evaluation=robustness_evaluation,
            )
        )

        return RobustnessEvaluatedResearchCycleResult(
            result=result,
            evaluation=evaluation,
            statistical_evaluation=statistical_evaluation,
            robustness_evaluation=robustness_evaluation,
            evidence=evidence,
            analysis=analysis,
            conclusion=conclusion,
            knowledge=knowledge,
        )

    def run_with_contradiction_evaluation(
        self,
        question: Question,
        hypothesis: Hypothesis,
        experiment: Experiment,
        executor: Callable[[Experiment], ExperimentResult],
    ) -> ContradictionEvaluatedResearchCycleResult:
        result = self.runner.run(experiment, executor)
        evaluation = self.evaluator.evaluate(result)

        statistical_evaluation = self.statistical_evaluator.evaluate(
            result
        )

        robustness_evaluation = self.robustness_evaluator.evaluate(
            result
        )

        contradiction_evaluation = self.contradiction_evaluator.evaluate(
            statistical_evaluation=statistical_evaluation,
            robustness_evaluation=robustness_evaluation,
        )

        evidence, analysis, conclusion, knowledge = (
            self.research_objects_builder.build(
                question=question,
                hypothesis=hypothesis,
                experiment=experiment,
                result=result,
                evaluation=evaluation,
                statistical_evaluation=statistical_evaluation,
                robustness_evaluation=robustness_evaluation,
                contradiction_evaluation=contradiction_evaluation,
            )
        )

        return ContradictionEvaluatedResearchCycleResult(
            result=result,
            evaluation=evaluation,
            statistical_evaluation=statistical_evaluation,
            robustness_evaluation=robustness_evaluation,
            contradiction_evaluation=contradiction_evaluation,
            evidence=evidence,
            analysis=analysis,
            conclusion=conclusion,
            knowledge=knowledge,
        )

    def run_with_hypothesis_decision(
        self,
        question: Question,
        hypothesis: Hypothesis,
        experiment: Experiment,
        executor: Callable[[Experiment], ExperimentResult],
    ) -> DecidedResearchCycleResult:
        result = self.runner.run(experiment, executor)
        evaluation = self.evaluator.evaluate(result)

        statistical_evaluation = self.statistical_evaluator.evaluate(
            result
        )

        robustness_evaluation = self.robustness_evaluator.evaluate(
            result
        )

        contradiction_evaluation = self.contradiction_evaluator.evaluate(
            statistical_evaluation=statistical_evaluation,
            robustness_evaluation=robustness_evaluation,
        )

        hypothesis_decision = (
            self.hypothesis_decision_evaluator.evaluate(
                hypothesis_id=hypothesis.id,
                experiment_evaluation=evaluation,
                statistical_evaluation=statistical_evaluation,
                robustness_evaluation=robustness_evaluation,
                contradiction_evaluation=contradiction_evaluation,
            )
        )

        evidence, analysis, conclusion, knowledge = (
            self.research_objects_builder.build(
                question=question,
                hypothesis=hypothesis,
                experiment=experiment,
                result=result,
                evaluation=evaluation,
                statistical_evaluation=statistical_evaluation,
                robustness_evaluation=robustness_evaluation,
                contradiction_evaluation=contradiction_evaluation,
                hypothesis_decision=hypothesis_decision,
            )
        )

        return DecidedResearchCycleResult(
            result=result,
            evaluation=evaluation,
            statistical_evaluation=statistical_evaluation,
            robustness_evaluation=robustness_evaluation,
            contradiction_evaluation=contradiction_evaluation,
            hypothesis_decision=hypothesis_decision,
            evidence=evidence,
            analysis=analysis,
            conclusion=conclusion,
            knowledge=knowledge,
        )

    def run_with_evidence_strength(
        self,
        question: Question,
        hypothesis: Hypothesis,
        experiment: Experiment,
        executor: Callable[[Experiment], ExperimentResult],
    ) -> EvidenceStrengthResearchCycleResult:
        (
            result,
            evaluation,
            statistical_evaluation,
            robustness_evaluation,
            contradiction_evaluation,
            evidence_strength_evaluation,
            hypothesis_decision,
        ) = self._run_complete_evaluation(
            hypothesis=hypothesis,
            experiment=experiment,
            executor=executor,
        )

        evidence, analysis, conclusion, knowledge = (
            self.research_objects_builder.build(
                question=question,
                hypothesis=hypothesis,
                experiment=experiment,
                result=result,
                evaluation=evaluation,
                statistical_evaluation=statistical_evaluation,
                robustness_evaluation=robustness_evaluation,
                contradiction_evaluation=contradiction_evaluation,
                evidence_strength_evaluation=(
                    evidence_strength_evaluation
                ),
                hypothesis_decision=hypothesis_decision,
            )
        )

        return EvidenceStrengthResearchCycleResult(
            result=result,
            evaluation=evaluation,
            statistical_evaluation=statistical_evaluation,
            robustness_evaluation=robustness_evaluation,
            contradiction_evaluation=contradiction_evaluation,
            evidence_strength_evaluation=(
                evidence_strength_evaluation
            ),
            hypothesis_decision=hypothesis_decision,
            evidence=evidence,
            analysis=analysis,
            conclusion=conclusion,
            knowledge=knowledge,
        )

    def run_with_next_experiment_selection(
        self,
        question: Question,
        hypothesis: Hypothesis,
        experiment: Experiment,
        executor: Callable[[Experiment], ExperimentResult],
    ) -> NextExperimentResearchCycleResult:
        (
            result,
            evaluation,
            statistical_evaluation,
            robustness_evaluation,
            contradiction_evaluation,
            evidence_strength_evaluation,
            hypothesis_decision,
        ) = self._run_complete_evaluation(
            hypothesis=hypothesis,
            experiment=experiment,
            executor=executor,
        )

        next_experiment_selection = self.next_experiment_selector.select(
            hypothesis_id=hypothesis.id,
            statistical_evaluation=statistical_evaluation,
            robustness_evaluation=robustness_evaluation,
            evidence_strength_evaluation=evidence_strength_evaluation,
            hypothesis_decision=hypothesis_decision,
        )

        evidence, analysis, conclusion, knowledge = (
            self.research_objects_builder.build(
                question=question,
                hypothesis=hypothesis,
                experiment=experiment,
                result=result,
                evaluation=evaluation,
                statistical_evaluation=statistical_evaluation,
                robustness_evaluation=robustness_evaluation,
                contradiction_evaluation=contradiction_evaluation,
                evidence_strength_evaluation=(
                    evidence_strength_evaluation
                ),
                hypothesis_decision=hypothesis_decision,
                next_experiment_selection=next_experiment_selection,
            )
        )

        return NextExperimentResearchCycleResult(
            result=result,
            evaluation=evaluation,
            statistical_evaluation=statistical_evaluation,
            robustness_evaluation=robustness_evaluation,
            contradiction_evaluation=contradiction_evaluation,
            evidence_strength_evaluation=(
                evidence_strength_evaluation
            ),
            hypothesis_decision=hypothesis_decision,
            next_experiment_selection=next_experiment_selection,
            evidence=evidence,
            analysis=analysis,
            conclusion=conclusion,
            knowledge=knowledge,
        )

    def _run_complete_evaluation(
        self,
        hypothesis: Hypothesis,
        experiment: Experiment,
        executor: Callable[[Experiment], ExperimentResult],
    ) -> tuple[
        ExperimentResult,
        ExperimentEvaluation,
        StatisticalEvaluation,
        RobustnessEvaluation,
        ContradictionEvaluation,
        EvidenceStrengthEvaluation,
        HypothesisDecision,
    ]:
        result = self.runner.run(experiment, executor)
        evaluation = self.evaluator.evaluate(result)

        statistical_evaluation = self.statistical_evaluator.evaluate(
            result
        )

        robustness_evaluation = self.robustness_evaluator.evaluate(
            result
        )

        contradiction_evaluation = self.contradiction_evaluator.evaluate(
            statistical_evaluation=statistical_evaluation,
            robustness_evaluation=robustness_evaluation,
        )

        evidence_strength_evaluation = (
            self.evidence_strength_evaluator.evaluate(
                experiment_evaluation=evaluation,
                statistical_evaluation=statistical_evaluation,
                robustness_evaluation=robustness_evaluation,
                contradiction_evaluation=contradiction_evaluation,
            )
        )

        hypothesis_decision = (
            self.hypothesis_decision_evaluator.evaluate(
                hypothesis_id=hypothesis.id,
                experiment_evaluation=evaluation,
                statistical_evaluation=statistical_evaluation,
                robustness_evaluation=robustness_evaluation,
                contradiction_evaluation=contradiction_evaluation,
            )
        )

        return (
            result,
            evaluation,
            statistical_evaluation,
            robustness_evaluation,
            contradiction_evaluation,
            evidence_strength_evaluation,
            hypothesis_decision,
        )

    def run_many(
        self,
        question: Question,
        hypothesis: Hypothesis,
        experiments: list[Experiment],
        executor: Callable[[Experiment], ExperimentResult],
    ) -> list[ResearchCycleResult]:
        return [
            self.run(
                question=question,
                hypothesis=hypothesis,
                experiment=experiment,
                executor=executor,
            )
            for experiment in experiments
        ]

    def run_many_with_evaluation(
        self,
        question: Question,
        hypothesis: Hypothesis,
        experiments: list[Experiment],
        executor: Callable[[Experiment], ExperimentResult],
    ) -> list[EvaluatedResearchCycleResult]:
        return [
            self.run_with_evaluation(
                question=question,
                hypothesis=hypothesis,
                experiment=experiment,
                executor=executor,
            )
            for experiment in experiments
        ]

    def run_many_with_evidence_strength(
        self,
        question: Question,
        hypothesis: Hypothesis,
        experiments: list[Experiment],
        executor: Callable[[Experiment], ExperimentResult],
    ) -> list[EvidenceStrengthResearchCycleResult]:
        return [
            self.run_with_evidence_strength(
                question=question,
                hypothesis=hypothesis,
                experiment=experiment,
                executor=executor,
            )
            for experiment in experiments
        ]

    def run_many_and_rank_evidence(
        self,
        question: Question,
        hypothesis: Hypothesis,
        experiments: list[Experiment],
        executor: Callable[[Experiment], ExperimentResult],
    ) -> tuple[
        list[EvidenceStrengthResearchCycleResult],
        list[RankedEvidence],
    ]:
        cycles = self.run_many_with_evidence_strength(
            question=question,
            hypothesis=hypothesis,
            experiments=experiments,
            executor=executor,
        )

        evidence_strength_evaluations = [
            cycle.evidence_strength_evaluation
            for cycle in cycles
        ]

        ranked_evidence = self.evidence_strength_ranker.rank(
            experiments=experiments,
            evaluations=evidence_strength_evaluations,
        )

        return cycles, ranked_evidence

    def run_many_and_select_best(
        self,
        question: Question,
        hypothesis: Hypothesis,
        experiments: list[Experiment],
        executor: Callable[[Experiment], ExperimentResult],
        metric: str,
        reverse: bool = True,
    ) -> tuple[list[ResearchCycleResult], RankedExperiment]:
        cycles = self.run_many(
            question=question,
            hypothesis=hypothesis,
            experiments=experiments,
            executor=executor,
        )

        results = [
            cycle.result
            for cycle in cycles
        ]

        best = self.comparator.best(
            experiments=experiments,
            results=results,
            metric=metric,
            reverse=reverse,
        )

        return cycles, best


