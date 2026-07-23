from __future__ import annotations

import pandas as pd

from src.research.baseline_comparator import (
    BaselineComparator,
)
from src.research.comparative_analysis import (
    ComparativeAnalysis,
)
from src.research.event_study_analyzer import (
    EventStudyAnalyzer,
)
from src.research.event_study_service import (
    EventStudyService,
)
from src.research.observations.observation import (
    Observation,
)
from src.research.outcome_specification import (
    ForwardReturnSpecification,
)
from src.research.unconditional_baseline_service import (
    UnconditionalBaselineService,
)


class ComparativeAnalysisService:
    """
    Runs a complete event study against an unconditional baseline.
    """

    def run(
        self,
        *,
        data: pd.DataFrame,
        observations: tuple[Observation, ...],
        specification: ForwardReturnSpecification,
    ) -> ComparativeAnalysis:
        candidate_result = EventStudyService().run(
            data=data,
            observations=observations,
            specification=specification,
        )

        if not candidate_result.observation_ids:
            raise ValueError(
                "candidate event study contains no "
                "complete observations"
            )

        baseline_result = (
            UnconditionalBaselineService().build(
                data=data,
                specification=specification,
            )
        )

        analyzer = EventStudyAnalyzer()
        candidate_statistics = analyzer.analyze(
            candidate_result
        )
        baseline_statistics = analyzer.analyze(
            baseline_result
        )
        comparisons = BaselineComparator().compare(
            candidate=candidate_statistics,
            baseline=baseline_statistics,
        )

        return ComparativeAnalysis(
            candidate_result=candidate_result,
            baseline_result=baseline_result,
            candidate_statistics=(
                candidate_statistics
            ),
            baseline_statistics=baseline_statistics,
            comparisons=comparisons,
        )
