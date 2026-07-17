from src.application.next_experiment_factory import (
    NextExperimentFactory,
)
from src.research import (
    Experiment,
    NextExperimentSelection,
)


def test_next_experiment_factory_creates_child_experiment():

    parent_experiment = Experiment(
        hypothesis_id="hypothesis-001",
        title="Parent experiment",
        description="Initial validation",
        parameters={
            "sample_size": 500,
        },
        tags=[
            "market",
        ],
    )

    selection = NextExperimentSelection(
        hypothesis_id="hypothesis-001",
        is_selected=True,
        action="increase_sample_size",
        priority="high",
        reason="Sample size requirement failed.",
        target_requirement="sample_size",
    )

    factory = NextExperimentFactory()

    child_experiment = factory.create(
        parent_experiment=parent_experiment,
        selection=selection,
    )

    assert (
        child_experiment.hypothesis_id
        == parent_experiment.hypothesis_id
    )

    assert child_experiment.id != parent_experiment.id

    assert (
        child_experiment.title
        == "Next experiment: increase sample size"
    )

    assert (
        child_experiment.description
        == "Sample size requirement failed."
    )

    assert child_experiment.parameters == {
        "sample_size": 500,
        "research_action": "increase_sample_size",
        "target_requirement": "sample_size",
    }

    assert child_experiment.tags == [
        "market",
        "next_experiment",
        "increase_sample_size",
    ]

    assert selection.id in child_experiment.notes


def test_next_experiment_factory_rejects_unselected_action():

    parent_experiment = Experiment(
        hypothesis_id="hypothesis-001",
    )

    selection = NextExperimentSelection(
        hypothesis_id="hypothesis-001",
        is_selected=False,
        action="none",
    )

    factory = NextExperimentFactory()

    try:
        factory.create(
            parent_experiment=parent_experiment,
            selection=selection,
        )
    except ValueError as error:
        assert str(error) == (
            "Next experiment selection must be selected."
        )
    else:
        raise AssertionError(
            "Expected ValueError for unselected action."
        )