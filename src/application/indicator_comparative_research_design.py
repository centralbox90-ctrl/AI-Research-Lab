from __future__ import annotations

from dataclasses import dataclass

from src.research.outcome_specification import (
    ForwardReturnSpecification,
)
from src.research.specification import (
    ResearchSpecification,
)


@dataclass(frozen=True, slots=True)
class IndicatorComparativeResearchDesign:
    """
    Predefined design for one comparative indicator study.
    """

    research_specification: ResearchSpecification
    outcome_specification: ForwardReturnSpecification
    baseline: str = "unconditional"

    def __post_init__(self) -> None:
        if not isinstance(
            self.research_specification,
            ResearchSpecification,
        ):
            raise TypeError(
                "research_specification must be a "
                "ResearchSpecification"
            )

        if not isinstance(
            self.outcome_specification,
            ForwardReturnSpecification,
        ):
            raise TypeError(
                "outcome_specification must be a "
                "ForwardReturnSpecification"
            )

        if not isinstance(self.baseline, str):
            raise TypeError(
                "baseline must be a string"
            )

        baseline = self.baseline.strip()

        if baseline != "unconditional":
            raise ValueError(
                "baseline must be 'unconditional'"
            )

        object.__setattr__(
            self,
            "baseline",
            baseline,
        )
