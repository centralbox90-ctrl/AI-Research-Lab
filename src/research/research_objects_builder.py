from src.research.analysis import Analysis
from src.research.conclusion import Conclusion
from src.research.contradiction_evaluation import ContradictionEvaluation
from src.research.evidence import Evidence
from src.research.evidence_strength_evaluation import EvidenceStrengthEvaluation
from src.research.experiment import Experiment
from src.research.experiment_evaluation import ExperimentEvaluation
from src.research.experiment_result import ExperimentResult
from src.research.hypothesis import Hypothesis
from src.research.hypothesis_decision import HypothesisDecision
from src.research.knowledge import Knowledge
from src.research.next_experiment_selection import NextExperimentSelection
from src.research.question import Question
from src.research.robustness_evaluation import RobustnessEvaluation
from src.research.statistical_evaluation import StatisticalEvaluation


class ResearchObjectsBuilder:
    def build(
        self,
        question: Question,
        hypothesis: Hypothesis,
        experiment: Experiment,
        result: ExperimentResult,
        evaluation: ExperimentEvaluation | None = None,
        statistical_evaluation: StatisticalEvaluation | None = None,
        robustness_evaluation: RobustnessEvaluation | None = None,
        contradiction_evaluation: ContradictionEvaluation | None = None,
        evidence_strength_evaluation: (
            EvidenceStrengthEvaluation | None
        ) = None,
        hypothesis_decision: HypothesisDecision | None = None,
        next_experiment_selection: NextExperimentSelection | None = None,
    ) -> tuple[
        Evidence,
        Analysis,
        Conclusion,
        Knowledge,
    ]:
        evidence = Evidence(
            experiment_id=experiment.id,
            title=f"Evidence for {experiment.title}",
            data=result.metrics,
            source="ExperimentRunner",
        )

        findings = {
            "success": result.success,
        }

        if evaluation is not None:
            findings.update(
                {
                    "result_is_valid": evaluation.is_valid,
                    "evidence_strength": evaluation.evidence_strength,
                    "evaluation_warnings": evaluation.warnings,
                }
            )

        if statistical_evaluation is not None:
            findings.update(
                {
                    "statistics_evaluated": (
                        statistical_evaluation.is_evaluated
                    ),
                    "statistically_significant": (
                        statistical_evaluation.is_significant
                    ),
                    "sample_size": statistical_evaluation.sample_size,
                    "mean": statistical_evaluation.mean,
                    "standard_deviation": (
                        statistical_evaluation.standard_deviation
                    ),
                    "standard_error": (
                        statistical_evaluation.standard_error
                    ),
                    "confidence_interval_lower": (
                        statistical_evaluation.confidence_interval_lower
                    ),
                    "confidence_interval_upper": (
                        statistical_evaluation.confidence_interval_upper
                    ),
                    "confidence_level": (
                        statistical_evaluation.confidence_level
                    ),
                    "null_mean": statistical_evaluation.null_mean,
                    "alternative": statistical_evaluation.alternative,
                    "significance_level": (
                        statistical_evaluation.significance_level
                    ),
                    "test_method": statistical_evaluation.test_method,
                    "test_statistic": (
                        statistical_evaluation.test_statistic
                    ),
                    "p_value": statistical_evaluation.p_value,
                    "effect_size": statistical_evaluation.effect_size,
                    "statistical_warnings": (
                        statistical_evaluation.warnings
                    ),
                }
            )

        if robustness_evaluation is not None:
            findings.update(
                {
                    "robustness_evaluated": (
                        robustness_evaluation.is_evaluated
                    ),
                    "is_robust": robustness_evaluation.is_robust,
                    "robustness_sample_size": (
                        robustness_evaluation.sample_size
                    ),
                    "positive_observation_ratio": (
                        robustness_evaluation
                        .positive_observation_ratio
                    ),
                    "negative_observation_ratio": (
                        robustness_evaluation
                        .negative_observation_ratio
                    ),
                    "zero_observation_ratio": (
                        robustness_evaluation.zero_observation_ratio
                    ),
                    "first_half_mean": (
                        robustness_evaluation.first_half_mean
                    ),
                    "second_half_mean": (
                        robustness_evaluation.second_half_mean
                    ),
                    "mean_shift": robustness_evaluation.mean_shift,
                    "direction_consistent": (
                        robustness_evaluation.direction_consistent
                    ),
                    "robustness_warnings": (
                        robustness_evaluation.warnings
                    ),
                }
            )

        if contradiction_evaluation is not None:
            findings.update(
                {
                    "contradictions_evaluated": (
                        contradiction_evaluation.is_evaluated
                    ),
                    "has_contradiction": (
                        contradiction_evaluation.has_contradiction
                    ),
                    "observed_direction": (
                        contradiction_evaluation.observed_direction
                    ),
                    "contradiction_statistically_significant": (
                        contradiction_evaluation
                        .statistically_significant
                    ),
                    "contradiction_robust": (
                        contradiction_evaluation.robust
                    ),
                    "significance_robustness_conflict": (
                        contradiction_evaluation
                        .significance_robustness_conflict
                    ),
                    "direction_robustness_conflict": (
                        contradiction_evaluation
                        .direction_robustness_conflict
                    ),
                    "contradiction_count": (
                        contradiction_evaluation.contradiction_count
                    ),
                    "contradiction_warnings": (
                        contradiction_evaluation.warnings
                    ),
                }
            )

        if evidence_strength_evaluation is not None:
            findings.update(
                {
                    "evidence_strength_evaluated": (
                        evidence_strength_evaluation.is_evaluated
                    ),
                    "evidence_strength_score": (
                        evidence_strength_evaluation.score
                    ),
                    "evidence_strength_level": (
                        evidence_strength_evaluation.level
                    ),
                    "evidence_strength_component_scores": (
                        evidence_strength_evaluation.component_scores
                    ),
                    "evidence_strength_warnings": (
                        evidence_strength_evaluation.warnings
                    ),
                }
            )

        if hypothesis_decision is not None:
            findings.update(
                {
                    "hypothesis_decision_evaluated": (
                        hypothesis_decision.is_evaluated
                    ),
                    "hypothesis_supported": (
                        hypothesis_decision.is_supported
                    ),
                    "decision_confidence": (
                        hypothesis_decision.confidence
                    ),
                    "decision_failed_requirements": (
                        hypothesis_decision.failed_requirements
                    ),
                    "decision_warnings": hypothesis_decision.warnings,
                }
            )

        if next_experiment_selection is not None:
            findings.update(
                {
                    "next_experiment_selected": (
                        next_experiment_selection.is_selected
                    ),
                    "next_experiment_action": (
                        next_experiment_selection.action
                    ),
                    "next_experiment_priority": (
                        next_experiment_selection.priority
                    ),
                    "next_experiment_reason": (
                        next_experiment_selection.reason
                    ),
                    "next_experiment_target_requirement": (
                        next_experiment_selection.target_requirement
                    ),
                    "next_experiment_recommendations": (
                        next_experiment_selection.recommendations
                    ),
                    "next_experiment_warnings": (
                        next_experiment_selection.warnings
                    ),
                }
            )

        analysis = Analysis(
            experiment_id=experiment.id,
            title=f"Analysis for {experiment.title}",
            findings=findings,
            interpretation=result.conclusion,
        )
        analysis.add_evidence(evidence.id)

        if evaluation is None:
            conclusion = Conclusion(
                analysis_id=analysis.id,
                hypothesis_id=hypothesis.id,
                title=f"Conclusion for {hypothesis.title}",
                statement=result.conclusion,
                supported=result.success,
                confidence=1.0 if result.success else 0.0,
                is_provisional=True,
                basis="Legacy result success flag",
            )

            knowledge = Knowledge(
                question_id=question.id,
                hypothesis_id=hypothesis.id,
                experiment_id=experiment.id,
                title=f"Knowledge from {hypothesis.title}",
                statement=conclusion.statement,
                confidence=conclusion.confidence,
                is_provisional=True,
                basis="Legacy result success flag",
            )

        elif statistical_evaluation is None:
            conclusion = Conclusion(
                analysis_id=analysis.id,
                hypothesis_id=hypothesis.id,
                title=f"Preliminary conclusion for {hypothesis.title}",
                statement=(
                    "Result passed basic validation, but the hypothesis "
                    "has not yet been statistically evaluated."
                    if evaluation.is_valid
                    else "Result failed basic validation."
                ),
                supported=False,
                confidence=0.0,
                is_provisional=True,
                basis="Basic result validation only",
                notes=result.conclusion,
            )

            knowledge = Knowledge(
                question_id=question.id,
                hypothesis_id=hypothesis.id,
                experiment_id=experiment.id,
                title=f"Preliminary knowledge from {hypothesis.title}",
                statement=conclusion.statement,
                confidence=0.0,
                is_provisional=True,
                basis="Basic result validation only",
            )

        elif robustness_evaluation is None:
            conclusion = Conclusion(
                analysis_id=analysis.id,
                hypothesis_id=hypothesis.id,
                title=(
                    f"Statistical preliminary conclusion "
                    f"for {hypothesis.title}"
                ),
                statement=(
                    "Inferential statistics were calculated, but "
                    "robustness and contradictions have not yet "
                    "been evaluated."
                    if statistical_evaluation.is_evaluated
                    else (
                        "Statistical evaluation could not be completed "
                        "because suitable observations were unavailable."
                    )
                ),
                supported=False,
                confidence=0.0,
                is_provisional=True,
                basis="Inferential statistics only",
                notes=result.conclusion,
            )

            knowledge = Knowledge(
                question_id=question.id,
                hypothesis_id=hypothesis.id,
                experiment_id=experiment.id,
                title=(
                    f"Statistical preliminary knowledge "
                    f"from {hypothesis.title}"
                ),
                statement=conclusion.statement,
                confidence=0.0,
                is_provisional=True,
                basis="Inferential statistics only",
            )

        elif contradiction_evaluation is None:
            conclusion = Conclusion(
                analysis_id=analysis.id,
                hypothesis_id=hypothesis.id,
                title=(
                    f"Robustness preliminary conclusion "
                    f"for {hypothesis.title}"
                ),
                statement=(
                    "Inferential statistics and robustness diagnostics "
                    "were calculated, but contradiction evaluation has "
                    "not yet been implemented."
                    if robustness_evaluation.is_evaluated
                    else (
                        "Robustness evaluation could not be completed "
                        "because suitable observations were unavailable."
                    )
                ),
                supported=False,
                confidence=0.0,
                is_provisional=True,
                basis="Inferential statistics and robustness diagnostics",
                notes=result.conclusion,
            )

            knowledge = Knowledge(
                question_id=question.id,
                hypothesis_id=hypothesis.id,
                experiment_id=experiment.id,
                title=(
                    f"Robustness preliminary knowledge "
                    f"from {hypothesis.title}"
                ),
                statement=conclusion.statement,
                confidence=0.0,
                is_provisional=True,
                basis=(
                    "Inferential statistics and robustness diagnostics"
                ),
            )

        elif hypothesis_decision is None:
            conclusion = Conclusion(
                analysis_id=analysis.id,
                hypothesis_id=hypothesis.id,
                title=(
                    f"Contradiction preliminary conclusion "
                    f"for {hypothesis.title}"
                ),
                statement=(
                    "Inferential statistics, robustness and "
                    "contradictions were evaluated. Final hypothesis "
                    "support decision is not implemented yet."
                    if contradiction_evaluation.is_evaluated
                    else (
                        "Contradiction evaluation could not be "
                        "completed."
                    )
                ),
                supported=False,
                confidence=0.0,
                is_provisional=True,
                basis=(
                    "Inferential statistics, robustness and "
                    "contradiction evaluation"
                ),
                notes=result.conclusion,
            )

            knowledge = Knowledge(
                question_id=question.id,
                hypothesis_id=hypothesis.id,
                experiment_id=experiment.id,
                title=(
                    f"Contradiction preliminary knowledge "
                    f"from {hypothesis.title}"
                ),
                statement=conclusion.statement,
                confidence=0.0,
                is_provisional=True,
                basis=(
                    "Inferential statistics, robustness and "
                    "contradiction evaluation"
                ),
            )

        else:
            decision_completed = hypothesis_decision.is_evaluated
            hypothesis_supported = (
                decision_completed
                and hypothesis_decision.is_supported
            )

            conclusion = Conclusion(
                analysis_id=analysis.id,
                hypothesis_id=hypothesis.id,
                title=f"Scientific conclusion for {hypothesis.title}",
                statement=(
                    "The hypothesis is supported by the completed "
                    "scientific evaluation pipeline."
                    if hypothesis_supported
                    else (
                        "The hypothesis is not supported by the "
                        "completed scientific evaluation pipeline."
                        if decision_completed
                        else (
                            "A final hypothesis support decision could "
                            "not be completed."
                        )
                    )
                ),
                supported=hypothesis_supported,
                confidence=hypothesis_decision.confidence,
                is_provisional=not decision_completed,
                basis=hypothesis_decision.basis,
                notes=result.conclusion,
            )

            knowledge = Knowledge(
                question_id=question.id,
                hypothesis_id=hypothesis.id,
                experiment_id=experiment.id,
                title=f"Scientific knowledge from {hypothesis.title}",
                statement=conclusion.statement,
                confidence=hypothesis_decision.confidence,
                is_provisional=not decision_completed,
                basis=hypothesis_decision.basis,
                notes=(
                    "Knowledge was produced from the completed "
                    "scientific hypothesis decision pipeline."
                    if decision_completed
                    else (
                        "Knowledge remains provisional because the "
                        "scientific hypothesis decision was incomplete."
                    )
                ),
            )

        return evidence, analysis, conclusion, knowledge