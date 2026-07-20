from src.research.evidence import Evidence


def test_evidence_defaults() -> None:
    evidence = Evidence()

    assert evidence.experiment_id == ""
    assert evidence.question_id == ""
    assert evidence.hypothesis_id == ""
    assert evidence.title == ""
    assert evidence.data == {}
    assert evidence.source == ""
    assert evidence.observation_ids == []
    assert evidence.description == ""
    assert evidence.supports_hypothesis is False
    assert evidence.confidence == 0.0
    assert evidence.tags == []
    assert evidence.notes == ""


def test_evidence_construction() -> None:
    evidence = Evidence(
        experiment_id="exp-1",
        question_id="q-1",
        hypothesis_id="h-1",
        title="Evidence",
        data={"profit": 12.5},
        source="ExperimentRunner",
        observation_ids=["obs-1", "obs-2"],
        description="Positive experiment",
        supports_hypothesis=True,
        confidence=0.91,
        tags=["research"],
        notes="verified",
    )

    assert evidence.experiment_id == "exp-1"
    assert evidence.question_id == "q-1"
    assert evidence.hypothesis_id == "h-1"
    assert evidence.data["profit"] == 12.5
    assert evidence.source == "ExperimentRunner"
    assert len(evidence.observation_ids) == 2
    assert evidence.supports_hypothesis is True
    assert evidence.confidence == 0.91


def test_evidence_is_mutable() -> None:
    evidence = Evidence()

    evidence.confidence = 0.75
    evidence.description = "updated"
    evidence.supports_hypothesis = True
    evidence.observation_ids.append("obs-1")

    assert evidence.confidence == 0.75
    assert evidence.description == "updated"
    assert evidence.supports_hypothesis is True
    assert evidence.observation_ids == ["obs-1"]


def test_summary_contains_core_information() -> None:
    evidence = Evidence(
        experiment_id="exp-1",
        title="Evidence",
        data={"profit": 10},
        source="Runner",
    )

    summary = evidence.summary()

    assert "Evidence" in summary
    assert "exp-1" in summary
    assert "Runner" in summary
    assert "1" in summary


def test_evidence_ids_are_unique() -> None:
    first = Evidence()
    second = Evidence()

    assert first.id != second.id


def test_data_default_is_not_shared() -> None:
    first = Evidence()
    second = Evidence()

    first.data["x"] = 1

    assert second.data == {}