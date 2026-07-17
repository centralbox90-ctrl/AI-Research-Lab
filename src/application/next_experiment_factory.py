from typing import Any

from src.research import (
    Experiment,
    NextExperimentSelection,
)


class NextExperimentFactory:
    """
    Creates a child experiment from a selected research action.

    The factory translates a NextExperimentSelection into an
    executable Experiment while preserving the parent hypothesis.
    """

    def create(
        self,
        parent_experiment: Experiment,
        selection: NextExperimentSelection,
    ) -> Experiment:
        if not selection.is_selected:
            raise ValueError(
                "Next experiment selection must be selected."
            )

        parameters = self._build_parameters(
            parent_parameters=parent_experiment.parameters,
            selection=selection,
        )

        return Experiment(
            hypothesis_id=parent_experiment.hypothesis_id,
            title=self._build_title(selection),
            description=self._build_description(selection),
            parameters=parameters,
            tags=[
                *parent_experiment.tags,
                "next_experiment",
                selection.action,
            ],
            notes=(
                "Created from next experiment selection "
                f"{selection.id}."
            ),
        )

    def _build_parameters(
        self,
        parent_parameters: dict[str, Any],
        selection: NextExperimentSelection,
    ) -> dict[str, Any]:
        parameters = dict(parent_parameters)

        parameters["research_action"] = selection.action

        if selection.target_requirement is not None:
            parameters["target_requirement"] = (
                selection.target_requirement
            )

        return parameters

    def _build_title(
        self,
        selection: NextExperimentSelection,
    ) -> str:
        return (
            "Next experiment: "
            f"{selection.action.replace('_', ' ')}"
        )

    def _build_description(
        self,
        selection: NextExperimentSelection,
    ) -> str:
        return selection.reason or (
            "Execute the selected next research action."
        )