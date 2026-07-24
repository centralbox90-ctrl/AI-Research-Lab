from __future__ import annotations

import json
from pathlib import Path

from src.application.indicator_comparative_hypothesis_evaluation_application import (
    IndicatorComparativeHypothesisEvaluationApplication,
)
from src.application.indicator_comparative_hypothesis_evaluation_request_loader import (
    IndicatorComparativeHypothesisEvaluationRequestLoader,
)
from src.cli.hypothesis_evaluation_presenter import (
    present_hypothesis_evaluation,
)


class RunIndicatorComparativeHypothesisEvaluationCommand:
    """
    CLI command for the complete comparative evaluation pipeline.
    """

    def __init__(
        self,
        *,
        application: (
            IndicatorComparativeHypothesisEvaluationApplication
        ),
        request_loader: (
            IndicatorComparativeHypothesisEvaluationRequestLoader
            | None
        ) = None,
    ) -> None:
        if not isinstance(
            application,
            IndicatorComparativeHypothesisEvaluationApplication,
        ):
            raise TypeError(
                "application must be an "
                "IndicatorComparativeHypothesisEvaluationApplication"
            )

        if (
            request_loader is not None
            and not isinstance(
                request_loader,
                IndicatorComparativeHypothesisEvaluationRequestLoader,
            )
        ):
            raise TypeError(
                "request_loader must be an "
                "IndicatorComparativeHypothesisEvaluationRequestLoader"
            )

        self._application = application
        self._request_loader = (
            request_loader
            or IndicatorComparativeHypothesisEvaluationRequestLoader()
        )

    def execute(
        self,
        request_path: str | Path,
        *,
        indent: int | None = 2,
    ) -> str:
        """
        Execute a JSON request and return the evaluation artifact.
        """

        request = self._request_loader.load(
            request_path
        )
        evaluation = self._application.run(
            hypothesis_id=request.hypothesis_id,
            requests=request.requests,
        )
        payload = present_hypothesis_evaluation(
            evaluation
        )

        return json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            indent=indent,
        )