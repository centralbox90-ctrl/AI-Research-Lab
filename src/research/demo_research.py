from src.research.question import Question
from src.research.hypothesis import Hypothesis


question = Question(
    title="Контртренд после трех свечей",
    description="Проверить вероятность отката после трех подряд растущих свечей.",
    research_type="Hypothesis Test",
    tags=["BTCUSDT", "CounterTrend", "1H"]
)

hypothesis = Hypothesis(
    question_id=question.id,
    title="Откат более 60%",
    description="После трех бычьих свечей вероятность отката превышает 60%.",
    expected_result="Probability > 60%",
    tags=["Williams", "CounterTrend"]
)

print(question.summary())
print()
print(hypothesis.summary())