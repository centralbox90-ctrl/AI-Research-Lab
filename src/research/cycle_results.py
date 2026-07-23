from dataclasses import dataclass
from typing import Any, Iterator

from src.research.analysis import Analysis
from src.research.conclusion import Conclusion
from src.research.contradiction_evaluation import (
    ContradictionEvaluation,
)
from src.research.legacy_evidence import (
    LegacyEvidence,
)
from src.research.evidence_strength_evaluation import (
    EvidenceStrengthEvaluation,
)
from src.research.experiment_evaluation import ExperimentEvaluation
from src.research.experiment_result import ExperimentResult
from src.research.hypothesis_decision import HypothesisDecision
from src.research.knowledge import Knowledge
from src.research.next_experiment_selection import (
    NextExperimentSelection,
)
from src.research.robustness_evaluation import RobustnessEvaluation
from src.research.statistical_evaluation import StatisticalEvaluation


class TupleCompatibleResult:
    """
    Base class for named research cycle results.

    Provides tuple-style unpacking and positional indexing for
    backward compatibility with the existing ResearchEngine API.
    """

    def as_tuple(self) -> tuple[Any, ...]:
        raise NotImplementedError

    def __iter__(self) -> Iterator[Any]:
        return iter(self.as_tuple())

    def __getitem__(self, index: int | slice) -> Any:
        return self.as_tuple()[index]

    def __len__(self) -> int:
        return len(self.as_tuple())


@dataclass
class ResearchCycleResult(TupleCompatibleResult):
    result: ExperimentResult
    evidence: LegacyEvidence
    analysis: Analysis
    conclusion: Conclusion
    knowledge: Knowledge

    def as_tuple(self) -> tuple[Any, ...]:
        return (
            self.result,
            self.evidence,
            self.analysis,
            self.conclusion,
            self.knowledge,
        )


@dataclass
class EvaluatedResearchCycleResult(TupleCompatibleResult):
    result: ExperimentResult
    evaluation: ExperimentEvaluation
    evidence: LegacyEvidence
    analysis: Analysis
    conclusion: Conclusion
    knowledge: Knowledge

    def as_tuple(self) -> tuple[Any, ...]:
        return (
            self.result,
            self.evaluation,
            self.evidence,
            self.analysis,
            self.conclusion,
            self.knowledge,
        )


@dataclass
class StatisticallyEvaluatedResearchCycleResult(
    TupleCompatibleResult
):
    result: ExperimentResult
    evaluation: ExperimentEvaluation
    statistical_evaluation: StatisticalEvaluation
    evidence: LegacyEvidence
    analysis: Analysis
    conclusion: Conclusion
    knowledge: Knowledge

    def as_tuple(self) -> tuple[Any, ...]:
        return (
            self.result,
            self.evaluation,
            self.statistical_evaluation,
            self.evidence,
            self.analysis,
            self.conclusion,
            self.knowledge,
        )


@dataclass
class RobustnessEvaluatedResearchCycleResult(
    TupleCompatibleResult
):
    result: ExperimentResult
    evaluation: ExperimentEvaluation
    statistical_evaluation: StatisticalEvaluation
    robustness_evaluation: RobustnessEvaluation
    evidence: LegacyEvidence
    analysis: Analysis
    conclusion: Conclusion
    knowledge: Knowledge

    def as_tuple(self) -> tuple[Any, ...]:
        return (
            self.result,
            self.evaluation,
            self.statistical_evaluation,
            self.robustness_evaluation,
            self.evidence,
            self.analysis,
            self.conclusion,
            self.knowledge,
        )


@dataclass
class ContradictionEvaluatedResearchCycleResult(
    TupleCompatibleResult
):
    result: ExperimentResult
    evaluation: ExperimentEvaluation
    statistical_evaluation: StatisticalEvaluation
    robustness_evaluation: RobustnessEvaluation
    contradiction_evaluation: ContradictionEvaluation
    evidence: LegacyEvidence
    analysis: Analysis
    conclusion: Conclusion
    knowledge: Knowledge

    def as_tuple(self) -> tuple[Any, ...]:
        return (
            self.result,
            self.evaluation,
            self.statistical_evaluation,
            self.robustness_evaluation,
            self.contradiction_evaluation,
            self.evidence,
            self.analysis,
            self.conclusion,
            self.knowledge,
        )


@dataclass
class DecidedResearchCycleResult(TupleCompatibleResult):
    result: ExperimentResult
    evaluation: ExperimentEvaluation
    statistical_evaluation: StatisticalEvaluation
    robustness_evaluation: RobustnessEvaluation
    contradiction_evaluation: ContradictionEvaluation
    hypothesis_decision: HypothesisDecision
    evidence: LegacyEvidence
    analysis: Analysis
    conclusion: Conclusion
    knowledge: Knowledge

    def as_tuple(self) -> tuple[Any, ...]:
        return (
            self.result,
            self.evaluation,
            self.statistical_evaluation,
            self.robustness_evaluation,
            self.contradiction_evaluation,
            self.hypothesis_decision,
            self.evidence,
            self.analysis,
            self.conclusion,
            self.knowledge,
        )


@dataclass
class EvidenceStrengthResearchCycleResult(
    TupleCompatibleResult
):
    result: ExperimentResult
    evaluation: ExperimentEvaluation
    statistical_evaluation: StatisticalEvaluation
    robustness_evaluation: RobustnessEvaluation
    contradiction_evaluation: ContradictionEvaluation
    evidence_strength_evaluation: EvidenceStrengthEvaluation
    hypothesis_decision: HypothesisDecision
    evidence: LegacyEvidence
    analysis: Analysis
    conclusion: Conclusion
    knowledge: Knowledge

    def as_tuple(self) -> tuple[Any, ...]:
        return (
            self.result,
            self.evaluation,
            self.statistical_evaluation,
            self.robustness_evaluation,
            self.contradiction_evaluation,
            self.evidence_strength_evaluation,
            self.hypothesis_decision,
            self.evidence,
            self.analysis,
            self.conclusion,
            self.knowledge,
        )


@dataclass
class NextExperimentResearchCycleResult(
    TupleCompatibleResult
):
    result: ExperimentResult
    evaluation: ExperimentEvaluation
    statistical_evaluation: StatisticalEvaluation
    robustness_evaluation: RobustnessEvaluation
    contradiction_evaluation: ContradictionEvaluation
    evidence_strength_evaluation: EvidenceStrengthEvaluation
    hypothesis_decision: HypothesisDecision
    next_experiment_selection: NextExperimentSelection
    evidence: LegacyEvidence
    analysis: Analysis
    conclusion: Conclusion
    knowledge: Knowledge

    def as_tuple(self) -> tuple[Any, ...]:
        return (
            self.result,
            self.evaluation,
            self.statistical_evaluation,
            self.robustness_evaluation,
            self.contradiction_evaluation,
            self.evidence_strength_evaluation,
            self.hypothesis_decision,
            self.next_experiment_selection,
            self.evidence,
            self.analysis,
            self.conclusion,
            self.knowledge,
        )