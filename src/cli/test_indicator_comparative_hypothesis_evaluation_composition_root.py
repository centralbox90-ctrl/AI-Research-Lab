from src.application.hypothesis_evaluation_application import (
    HypothesisEvaluationApplication,
)
from src.application.hypothesis_evaluation_artifact_envelope_factory import (
    HypothesisEvaluationArtifactEnvelopeFactory,
)
from src.application.research_artifact_envelope import (
    ResearchArtifactEnvelopeFactory,
)
from src.application.indicator_comparative_finding_application import (
    IndicatorComparativeFindingApplication,
)
from src.application.indicator_comparative_hypothesis_evaluation_application import (
    IndicatorComparativeHypothesisEvaluationApplication,
)
from src.cli.indicator_comparative_hypothesis_evaluation_composition_root import (
    build_default_indicator_comparative_hypothesis_evaluation_application,
    build_default_indicator_comparative_hypothesis_evaluation_command,
)
from src.cli.run_indicator_comparative_hypothesis_evaluation_command import (
    RunIndicatorComparativeHypothesisEvaluationCommand,
)
from src.research.comparative_evaluation_plan import (
    ComparativeEvaluationPlan,
)
from src.research.hypothesis_evaluation_plan import (
    HypothesisEvaluationPlan,
)


class StubDatasetProvider:
    def load(self, specification: object) -> object:
        raise AssertionError(
            "load must not run during composition"
        )


def test_builds_application_with_declared_plans(
) -> None:
    comparative_plan = ComparativeEvaluationPlan(
        random_seed=23,
    )
    hypothesis_plan = HypothesisEvaluationPlan(
        version="hypothesis-evaluation-composed",
        supported_confidence_threshold=0.8,
        partially_supported_confidence_threshold=0.6,
        rejected_confidence_threshold=0.85,
        minimum_decisive_findings=3,
    )

    application = (
        build_default_indicator_comparative_hypothesis_evaluation_application(
            data_provider=StubDatasetProvider(),
            comparative_evaluation_plan=comparative_plan,
            hypothesis_evaluation_plan=hypothesis_plan,
        )
    )

    assert isinstance(
        application,
        IndicatorComparativeHypothesisEvaluationApplication,
    )
    assert isinstance(
        application._finding_application,
        IndicatorComparativeFindingApplication,
    )
    assert (
        application
        ._finding_application
        ._evidence_application
        ._research_application
        ._evaluation_plan
        is comparative_plan
    )
    assert isinstance(
        application._hypothesis_evaluation_application,
        HypothesisEvaluationApplication,
    )
    assert (
        application
        ._hypothesis_evaluation_application
        ._hypothesis_evaluator
        ._plan
        is hypothesis_plan
    )


def test_builds_application_with_default_plans(
) -> None:
    application = (
        build_default_indicator_comparative_hypothesis_evaluation_application(
            data_provider=StubDatasetProvider(),
        )
    )
    comparative_plan = (
        application
        ._finding_application
        ._evidence_application
        ._research_application
        ._evaluation_plan
    )
    hypothesis_plan = (
        application
        ._hypothesis_evaluation_application
        ._hypothesis_evaluator
        ._plan
    )

    assert isinstance(
        comparative_plan,
        ComparativeEvaluationPlan,
    )
    assert isinstance(
        hypothesis_plan,
        HypothesisEvaluationPlan,
    )
    assert comparative_plan.random_seed == 0
    assert hypothesis_plan.version == (
        "hypothesis-evaluation-v1"
    )


def test_builds_command_with_declared_plans(
) -> None:
    comparative_plan = ComparativeEvaluationPlan(
        random_seed=29,
    )
    hypothesis_plan = HypothesisEvaluationPlan(
        version="hypothesis-evaluation-command",
        minimum_decisive_findings=4,
    )
    envelope_factory = (
        HypothesisEvaluationArtifactEnvelopeFactory(
            envelope_factory=(
                ResearchArtifactEnvelopeFactory(
                    producer="composition-test",
                    producer_version="test",
                )
            )
        )
    )

    command = (
        build_default_indicator_comparative_hypothesis_evaluation_command(
            data_provider=StubDatasetProvider(),
            comparative_evaluation_plan=(
                comparative_plan
            ),
            hypothesis_evaluation_plan=(
                hypothesis_plan
            ),
            artifact_envelope_factory=(
                envelope_factory
            ),
        )
    )

    assert isinstance(
        command,
        RunIndicatorComparativeHypothesisEvaluationCommand,
    )
    assert (
        command
        ._application
        ._finding_application
        ._evidence_application
        ._research_application
        ._evaluation_plan
        is comparative_plan
    )
    assert (
        command
        ._application
        ._hypothesis_evaluation_application
        ._hypothesis_evaluator
        ._plan
        is hypothesis_plan
    )

    assert (
        command._artifact_envelope_factory
        is envelope_factory
    )
