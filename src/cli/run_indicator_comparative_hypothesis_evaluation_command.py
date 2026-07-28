from __future__ import annotations

import json
from pathlib import Path

from src.application.indicator_comparative_hypothesis_evaluation_application import (
    IndicatorComparativeHypothesisEvaluationApplication,
)
from src.application.indicator_comparative_hypothesis_evaluation_request_loader import (
    IndicatorComparativeHypothesisEvaluationRequestLoader,
)
from src.application.promote_hypothesis_evaluation_to_knowledge import (
    PromoteHypothesisEvaluationToKnowledge,
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
        promotion_application: (
            PromoteHypothesisEvaluationToKnowledge
            | None
        ) = None,
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
            promotion_application is not None
            and not isinstance(
                promotion_application,
                PromoteHypothesisEvaluationToKnowledge,
            )
        ):
            raise TypeError(
                "promotion_application must be a "
                "PromoteHypothesisEvaluationToKnowledge "
                "or None"
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
        self._promotion_application = (
            promotion_application
        )
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
        promotion = request.knowledge_promotion

        if promotion is not None:
            if self._promotion_application is None:
                raise ValueError(
                    "Knowledge promotion is not configured"
                )

            revision = (
                self._promotion_application.run(
                    evaluation=evaluation,
                    knowledge_id=(
                        promotion.knowledge_id
                    ),
                    statement=promotion.statement,
                    applicability=(
                        promotion.applicability
                    ),
                    limitations=(
                        promotion.limitations
                    ),
                    provenance=promotion.provenance,
                )
            )
            payload["artifact_version"] = 2
            payload["knowledge_revision"] = {
                **revision.to_dict(),
                "fingerprint": (
                    revision.fingerprint
                ),
            }

        return json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            indent=indent,
        )