from __future__ import annotations

import json
from pathlib import Path

from src.application.hypothesis_evaluation_artifact_envelope_factory import (
    HypothesisEvaluationArtifactEnvelopeFactory,
)
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
        artifact_envelope_factory: (
            HypothesisEvaluationArtifactEnvelopeFactory
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
            artifact_envelope_factory is not None
            and not isinstance(
                artifact_envelope_factory,
                HypothesisEvaluationArtifactEnvelopeFactory,
            )
        ):
            raise TypeError(
                "artifact_envelope_factory must be a "
                "HypothesisEvaluationArtifactEnvelopeFactory "
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
        self._artifact_envelope_factory = (
            artifact_envelope_factory
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
            correlation_id=request.correlation_id,
        )
        promotion = request.knowledge_promotion
        revision = None

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

        if self._artifact_envelope_factory is not None:
            envelope = (
                self._artifact_envelope_factory.create(
                    evaluation=evaluation,
                    correlation_id=(
                        request.correlation_id
                    ),
                    knowledge_revision=revision,
                )
            )

            return json.dumps(
                envelope.to_dict(),
                ensure_ascii=False,
                sort_keys=True,
                indent=indent,
            )

        payload = present_hypothesis_evaluation(
            evaluation
        )

        if revision is not None:
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