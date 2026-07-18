from src.research.engine import ResearchEngine
from src.research.experiment import Experiment
from src.research.experiment_result import ExperimentResult
from src.research.hypothesis import Hypothesis
from src.research.question import Question
from src.research.research_campaign import ResearchCampaign
from src.research.research_types import ResearchStatus


def build_question() -> Question:
    return Question(
        title="Campaign question",
    )


def build_hypothesis(
    question: Question,
) -> Hypothesis:
    return Hypothesis(
        question_id=question.id,
        title="Campaign hypothesis",
    )


def build_experiment(
    hypothesis: Hypothesis,
    title: str,
) -> Experiment:
    return Experiment(
        hypothesis_id=hypothesis.id,
        title=title,
    )


def successful_executor(
    experiment: Experiment,
) -> ExperimentResult:
    return ExperimentResult(
        experiment_id=experiment.id,
        success=True,
        metrics={
            "profit": 10,
        },
        conclusion="supported",
    )


def failing_executor(
    experiment: Experiment,
) -> ExperimentResult:
    raise RuntimeError(
        "experiment failed"
    )


def test_run_campaign_completes_successfully() -> None:
    question = build_question()
    hypothesis = build_hypothesis(question)

    experiment = build_experiment(
        hypothesis,
        "experiment-001",
    )

    campaign = ResearchCampaign(
        title="Campaign",
        hypothesis_id=hypothesis.id,
    )

    campaign.add_experiment(
        experiment.id,
    )

    results = ResearchEngine().run_campaign(
        question=question,
        hypothesis=hypothesis,
        campaign=campaign,
        experiments=[
            experiment,
        ],
        executor=successful_executor,
    )

    assert len(results) == 1
    assert results[0].result.success is True
    assert campaign.status == ResearchStatus.COMPLETED


def test_run_campaign_marks_failed_on_error() -> None:
    question = build_question()
    hypothesis = build_hypothesis(question)

    experiment = build_experiment(
        hypothesis,
        "experiment-failed",
    )

    campaign = ResearchCampaign(
        title="Failed campaign",
        hypothesis_id=hypothesis.id,
    )

    campaign.add_experiment(
        experiment.id,
    )

    try:
        ResearchEngine().run_campaign(
            question=question,
            hypothesis=hypothesis,
            campaign=campaign,
            experiments=[
                experiment,
            ],
            executor=failing_executor,
        )

        assert False

    except RuntimeError:
        pass

    assert campaign.status == ResearchStatus.FAILED


def test_run_campaign_rejects_unknown_experiment() -> None:
    question = build_question()
    hypothesis = build_hypothesis(question)

    campaign = ResearchCampaign(
        title="Campaign",
        hypothesis_id=hypothesis.id,
    )

    experiment = build_experiment(
        hypothesis,
        "not-registered",
    )

    try:
        ResearchEngine().run_campaign(
            question=question,
            hypothesis=hypothesis,
            campaign=campaign,
            experiments=[
                experiment,
            ],
            executor=successful_executor,
        )

        assert False

    except ValueError:
        pass