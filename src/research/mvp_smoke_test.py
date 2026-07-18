from src.research.experiment import Experiment
from src.research.experiment_result import ExperimentResult
from src.research.experiment_runner import ExperimentRunner
from src.research.hypothesis import Hypothesis
from src.research.knowledge import Knowledge
from src.research.question import Question
from src.research.research_campaign import ResearchCampaign
from src.research.research_plan import ResearchPlan


question = Question(
    title="Counter-trend after three candles",
    description=(
        "Check pullback probability after three bullish candles."
    ),
    tags=[
        "BTCUSDT",
        "1H",
    ],
)


hypothesis = Hypothesis(
    question_id=question.id,
    title="Pullback probability above 60%",
    expected_result="Probability > 60%",
)


experiment = Experiment(
    hypothesis_id=hypothesis.id,
    title="Williams and ADX test",
    parameters={
        "williams_period": 14,
        "adx_period": 18,
    },
)


campaign = ResearchCampaign(
    title="Counter-trend campaign",
    hypothesis_id=hypothesis.id,
)

campaign.add_experiment(
    experiment.id,
)


plan = ResearchPlan(
    question_id=question.id,
    title="Counter-trend research plan",
)

plan.add_campaign(
    campaign.id,
)


def execute(
    current_experiment: Experiment,
) -> ExperimentResult:
    return ExperimentResult(
        experiment_id=current_experiment.id,
        success=True,
        metrics={
            "profit": 27.0,
            "drawdown": 5.0,
            "win_rate": 61.0,
        },
        conclusion="Hypothesis supported",
    )


result = ExperimentRunner().run(
    experiment,
    execute,
)


knowledge = Knowledge(
    question_id=question.id,
    hypothesis_id=hypothesis.id,
    experiment_id=experiment.id,
    title="Counter-trend pattern",
    statement=result.conclusion,
    confidence=0.82,
)


print(question.summary())
print()

print(hypothesis.summary())
print()

print(campaign.summary())
print()

print(plan.summary())
print()

print(experiment.summary())
print()

print(result.summary())
print()

print(knowledge.summary())
