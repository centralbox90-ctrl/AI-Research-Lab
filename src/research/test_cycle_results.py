from src.research.analysis import Analysis
from src.research.conclusion import Conclusion
from src.research.cycle_results import (
    EvidenceStrengthResearchCycleResult,
    NextExperimentResearchCycleResult,
    ResearchCycleResult,
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
from src.research.contradiction_evaluation import (
    ContradictionEvaluation,
)


def test_research_cycle_result_supports_named_and_tuple_access() -> None:
    result = ExperimentResult(experiment_id="experiment-1")
    evidence = LegacyEvidence(experiment_id="experiment-1")
    analysis = Analysis(experiment_id="experiment-1")
    conclusion = Conclusion(hypothesis_id="hypothesis-1")
    knowledge = Knowledge(
        question_id="question-1",
        hypothesis_id="hypothesis-1",
        experiment_id="experiment-1",
    )

    cycle = ResearchCycleResult(
        result=result,
        evidence=evidence,
        analysis=analysis,
        conclusion=conclusion,
        knowledge=knowledge,
    )

    assert cycle.result is result
    assert cycle.evidence is evidence
    assert cycle.analysis is analysis
    assert cycle.conclusion is conclusion
    assert cycle.knowledge is knowledge

    assert len(cycle) == 5
    assert cycle[0] is result
    assert cycle[1] is evidence
    assert cycle[2] is analysis
    assert cycle[3] is conclusion
    assert cycle[4] is knowledge

    unpacked = tuple(cycle)

    assert unpacked == (
        result,
        evidence,
        analysis,
        conclusion,
        knowledge,
    )


def test_evidence_strength_cycle_result_preserves_public_order() -> None:
    result = ExperimentResult(experiment_id="experiment-1")
    evaluation = ExperimentEvaluation(
        experiment_id="experiment-1",
    )
    statistical_evaluation = StatisticalEvaluation(
        experiment_id="experiment-1",
    )
    robustness_evaluation = RobustnessEvaluation(
        experiment_id="experiment-1",
    )
    contradiction_evaluation = ContradictionEvaluation(
        experiment_id="experiment-1",
    )
    evidence_strength_evaluation = EvidenceStrengthEvaluation(
        experiment_id="experiment-1",
    )
    hypothesis_decision = HypothesisDecision(
        experiment_id="experiment-1",
        hypothesis_id="hypothesis-1",
    )
    evidence = LegacyEvidence(experiment_id="experiment-1")
    analysis = Analysis(experiment_id="experiment-1")
    conclusion = Conclusion(hypothesis_id="hypothesis-1")
    knowledge = Knowledge(
        question_id="question-1",
        hypothesis_id="hypothesis-1",
        experiment_id="experiment-1",
    )

    cycle = EvidenceStrengthResearchCycleResult(
        result=result,
        evaluation=evaluation,
        statistical_evaluation=statistical_evaluation,
        robustness_evaluation=robustness_evaluation,
        contradiction_evaluation=contradiction_evaluation,
        evidence_strength_evaluation=evidence_strength_evaluation,
        hypothesis_decision=hypothesis_decision,
        evidence=evidence,
        analysis=analysis,
        conclusion=conclusion,
        knowledge=knowledge,
    )

    assert cycle.result is result
    assert cycle.evaluation is evaluation
    assert cycle.statistical_evaluation is statistical_evaluation
    assert cycle.robustness_evaluation is robustness_evaluation
    assert cycle.contradiction_evaluation is contradiction_evaluation
    assert (
        cycle.evidence_strength_evaluation
        is evidence_strength_evaluation
    )
    assert cycle.hypothesis_decision is hypothesis_decision
    assert cycle.evidence is evidence
    assert cycle.analysis is analysis
    assert cycle.conclusion is conclusion
    assert cycle.knowledge is knowledge

    assert len(cycle) == 11
    assert cycle[0] is result
    assert cycle[1] is evaluation
    assert cycle[2] is statistical_evaluation
    assert cycle[3] is robustness_evaluation
    assert cycle[4] is contradiction_evaluation
    assert cycle[5] is evidence_strength_evaluation
    assert cycle[6] is hypothesis_decision
    assert cycle[7] is evidence
    assert cycle[8] is analysis
    assert cycle[9] is conclusion
    assert cycle[10] is knowledge

    assert cycle[5:8] == (
        evidence_strength_evaluation,
        hypothesis_decision,
        evidence,
    )


def test_next_experiment_cycle_result_exposes_selection() -> None:
    result = ExperimentResult(experiment_id="experiment-1")
    evaluation = ExperimentEvaluation(
        experiment_id="experiment-1",
    )
    statistical_evaluation = StatisticalEvaluation(
        experiment_id="experiment-1",
    )
    robustness_evaluation = RobustnessEvaluation(
        experiment_id="experiment-1",
    )
    contradiction_evaluation = ContradictionEvaluation(
        experiment_id="experiment-1",
    )
    evidence_strength_evaluation = EvidenceStrengthEvaluation(
        experiment_id="experiment-1",
    )
    hypothesis_decision = HypothesisDecision(
        experiment_id="experiment-1",
        hypothesis_id="hypothesis-1",
    )
    next_experiment_selection = NextExperimentSelection(
        hypothesis_id="hypothesis-1",
        is_selected=True,
        action="replicate_experiment",
        priority="low",
    )
    evidence = LegacyEvidence(experiment_id="experiment-1")
    analysis = Analysis(experiment_id="experiment-1")
    conclusion = Conclusion(hypothesis_id="hypothesis-1")
    knowledge = Knowledge(
        question_id="question-1",
        hypothesis_id="hypothesis-1",
        experiment_id="experiment-1",
    )

    cycle = NextExperimentResearchCycleResult(
        result=result,
        evaluation=evaluation,
        statistical_evaluation=statistical_evaluation,
        robustness_evaluation=robustness_evaluation,
        contradiction_evaluation=contradiction_evaluation,
        evidence_strength_evaluation=evidence_strength_evaluation,
        hypothesis_decision=hypothesis_decision,
        next_experiment_selection=next_experiment_selection,
        evidence=evidence,
        analysis=analysis,
        conclusion=conclusion,
        knowledge=knowledge,
    )

    assert cycle.next_experiment_selection is next_experiment_selection
    assert cycle.next_experiment_selection.action == "replicate_experiment"
    assert cycle.next_experiment_selection.priority == "low"

    assert len(cycle) == 12
    assert cycle[7] is next_experiment_selection
    assert tuple(cycle)[7] is next_experiment_selection