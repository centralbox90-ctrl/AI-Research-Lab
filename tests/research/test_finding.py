from datetime import datetime

from src.research.finding import Finding


def test_finding_creates_with_defaults() -> None:
    finding = Finding()

    assert finding.id
    assert finding.question_id == ""
    assert finding.hypothesis_id == ""
    assert finding.experiment_id == ""
    assert finding.evidence_id == ""
    assert finding.title == ""
    assert finding.conclusion == ""
    assert finding.supports_hypothesis is False
    assert finding.confidence == 0.0
    assert isinstance(finding.created_at, datetime)
    assert finding.notes == ""


def test_finding_accepts_research_context() -> None:
    finding = Finding(
        id="finding-001",
        question_id="question-001",
        hypothesis_id="hypothesis-001",
        experiment_id="experiment-001",
        evidence_id="evidence-001",
        title="Williams %R finding",
        conclusion="The hypothesis is supported.",
        supports_hypothesis=True,
        confidence=0.82,
        notes="Observed across multiple datasets.",
    )

    assert finding.id == "finding-001"
    assert finding.question_id == "question-001"
    assert finding.hypothesis_id == "hypothesis-001"
    assert finding.experiment_id == "experiment-001"
    assert finding.evidence_id == "evidence-001"
    assert finding.title == "Williams %R finding"
    assert finding.conclusion == "The hypothesis is supported."
    assert finding.supports_hypothesis is True
    assert finding.confidence == 0.82
    assert finding.notes == "Observed across multiple datasets."


def test_finding_is_mutable() -> None:
    finding = Finding(
        confidence=0.35,
        supports_hypothesis=False,
    )

    finding.confidence = 0.91
    finding.supports_hypothesis = True

    assert finding.confidence == 0.91
    assert finding.supports_hypothesis is True


def test_finding_summary_contains_context() -> None:
    finding = Finding(
        id="finding-001",
        question_id="question-001",
        hypothesis_id="hypothesis-001",
        experiment_id="experiment-001",
        evidence_id="evidence-001",
        title="Williams investigation",
        conclusion="The effect is statistically significant.",
        supports_hypothesis=True,
        confidence=0.95,
    )

    summary = finding.summary()

    assert "Finding: Williams investigation" in summary
    assert "ID: finding-001" in summary
    assert "Question: question-001" in summary
    assert "Hypothesis: hypothesis-001" in summary
    assert "Experiment: experiment-001" in summary
    assert "Evidence: evidence-001" in summary
    assert "Supports hypothesis: True" in summary
    assert "Confidence: 0.95" in summary
    assert "Conclusion: The effect is statistically significant." in summary


def test_finding_summary_uses_none_for_empty_conclusion() -> None:
    finding = Finding(
        title="Incomplete finding",
    )

    summary = finding.summary()

    assert "Conclusion: None" in summary


def test_finding_unique_ids() -> None:
    first = Finding()
    second = Finding()

    assert first.id != second.id