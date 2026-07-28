from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import pytest

from src.application.indicator_comparative_hypothesis_evaluation_application import (
    IndicatorComparativeHypothesisEvaluationApplication,
)
from src.application.indicator_comparative_hypothesis_evaluation_request_loader import (
    IndicatorComparativeHypothesisEvaluationRequestLoader,
    KnowledgePromotionRequest,
)
from src.application.promote_hypothesis_evaluation_to_knowledge import (
    PromoteHypothesisEvaluationToKnowledge,
)
from src.cli.run_indicator_comparative_hypothesis_evaluation_command import (
    RunIndicatorComparativeHypothesisEvaluationCommand,
)
from src.research.hypothesis_evaluation import (
    HypothesisEvaluation,
    HypothesisEvaluationState,
)
from src.research.knowledge_item import (
    KnowledgeItem,
)
from src.research.knowledge_revision import (
    KnowledgeRevision,
)


@dataclass(frozen=True)
class StubLoadedRequest:
    hypothesis_id: str
    requests: tuple[object, ...]
    knowledge_promotion: (
        KnowledgePromotionRequest | None
    ) = None


class StubRequestLoader(
    IndicatorComparativeHypothesisEvaluationRequestLoader
):
    def __init__(
        self,
        result: StubLoadedRequest,
    ) -> None:
        self.result = result
        self.paths: list[str | Path] = []

    def load(
        self,
        path: str | Path,
    ) -> StubLoadedRequest:
        self.paths.append(path)

        return self.result


class StubApplication(
    IndicatorComparativeHypothesisEvaluationApplication
):
    def __init__(
        self,
        result: HypothesisEvaluation,
    ) -> None:
        self.result = result
        self.calls: list[
            tuple[str, tuple[object, ...]]
        ] = []

    def run(
        self,
        *,
        hypothesis_id: str,
        requests: tuple[object, ...],
    ) -> HypothesisEvaluation:
        self.calls.append(
            (
                hypothesis_id,
                requests,
            )
        )

        return self.result


class StubPromotionApplication(
    PromoteHypothesisEvaluationToKnowledge
):
    def __init__(
        self,
        result: KnowledgeRevision,
    ) -> None:
        self.result = result
        self.calls: list[
            dict[str, object]
        ] = []

    def run(
        self,
        *,
        evaluation: HypothesisEvaluation,
        knowledge_id: str,
        statement: str,
        applicability: tuple[str, ...],
        limitations: tuple[str, ...],
        provenance: tuple[
            tuple[str, str],
            ...,
        ],
    ) -> KnowledgeRevision:
        self.calls.append(
            {
                "evaluation": evaluation,
                "knowledge_id": knowledge_id,
                "statement": statement,
                "applicability": applicability,
                "limitations": limitations,
                "provenance": provenance,
            }
        )

        return self.result


def build_evaluation() -> HypothesisEvaluation:
    return HypothesisEvaluation(
        id=(
            "hypothesis-evaluation:"
            "sha256:command-example"
        ),
        hypothesis_id="hypothesis-rsi",
        state=HypothesisEvaluationState.SUPPORTED,
        confidence=0.82,
        finding_refs=(
            "finding-a",
            "finding-b",
        ),
        rationale=(
            "replicated findings support the hypothesis",
        ),
        limitations=(),
        provenance=(
            (
                "evaluation_plan_version",
                "hypothesis-evaluation-v1",
            ),
        ),
    )


def build_revision() -> KnowledgeRevision:
    return KnowledgeRevision(
        item=KnowledgeItem(
            id="knowledge-rsi",
            statement=(
                "RSI effect persists across markets."
            ),
            confidence=0.82,
            applicability=("liquid FX",),
            limitations=("generated data",),
            supporting_findings=(
                "finding-a",
                "finding-b",
            ),
            version=1,
            provenance=(("producer", "test"),),
        ),
        valid_from=datetime(
            2026,
            7,
            28,
            12,
            0,
            tzinfo=UTC,
        ),
        change_reason=(
            "Promoted from hypothesis evaluation."
        ),
        supersedes_version=None,
    )


def build_command(
) -> tuple[
    RunIndicatorComparativeHypothesisEvaluationCommand,
    StubApplication,
    StubRequestLoader,
]:
    loaded_request = StubLoadedRequest(
        hypothesis_id="hypothesis-rsi",
        requests=(
            "request-a",
            "request-b",
        ),
    )
    loader = StubRequestLoader(
        loaded_request
    )
    application = StubApplication(
        build_evaluation()
    )

    return (
        RunIndicatorComparativeHypothesisEvaluationCommand(
            application=application,
            request_loader=loader,
        ),
        application,
        loader,
    )


def test_executes_request_and_returns_json_artifact(
) -> None:
    command, application, loader = build_command()
    request_path = Path("evaluation-request.json")

    rendered = command.execute(
        request_path
    )
    payload = json.loads(rendered)

    assert loader.paths == [
        request_path,
    ]
    assert application.calls == [
        (
            "hypothesis-rsi",
            (
                "request-a",
                "request-b",
            ),
        )
    ]
    assert payload["artifact_type"] == (
        "hypothesis_evaluation"
    )
    assert payload["artifact_version"] == 1
    assert payload["evaluation"]["state"] == (
        "supported"
    )
    assert payload["evaluation"]["confidence"] == 0.82
    assert payload["evaluation"]["fingerprint"] == (
        application.result.fingerprint
    )


def test_supports_compact_json() -> None:
    command, _, _ = build_command()

    rendered = command.execute(
        "evaluation-request.json",
        indent=None,
    )

    assert "\n" not in rendered
    assert json.loads(rendered)[
        "evaluation"
    ]["hypothesis_id"] == "hypothesis-rsi"


def test_rejects_invalid_application() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "application must be an "
            "IndicatorComparativeHypothesisEvaluationApplication"
        ),
    ):
        RunIndicatorComparativeHypothesisEvaluationCommand(
            application=object(),
        )


def test_rejects_invalid_request_loader() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "request_loader must be an "
            "IndicatorComparativeHypothesisEvaluationRequestLoader"
        ),
    ):
        RunIndicatorComparativeHypothesisEvaluationCommand(
            application=StubApplication(
                build_evaluation()
            ),
            request_loader=object(),
        )

def test_executes_requested_knowledge_promotion(
) -> None:
    promotion = KnowledgePromotionRequest(
        knowledge_id="knowledge-rsi",
        statement=(
            "RSI effect persists across markets."
        ),
        applicability=("liquid FX",),
        limitations=("generated data",),
        provenance=(("producer", "request"),),
    )
    loaded_request = StubLoadedRequest(
        hypothesis_id="hypothesis-rsi",
        requests=("request-a",),
        knowledge_promotion=promotion,
    )
    loader = StubRequestLoader(
        loaded_request
    )
    evaluation_application = StubApplication(
        build_evaluation()
    )
    promotion_application = (
        StubPromotionApplication(
            build_revision()
        )
    )
    command = (
        RunIndicatorComparativeHypothesisEvaluationCommand(
            application=evaluation_application,
            promotion_application=(
                promotion_application
            ),
            request_loader=loader,
        )
    )

    rendered = command.execute(
        "evaluation-request.json"
    )
    payload = json.loads(rendered)

    assert len(promotion_application.calls) == 1
    call = promotion_application.calls[0]
    assert call["evaluation"] is (
        evaluation_application.result
    )
    assert call["knowledge_id"] == (
        "knowledge-rsi"
    )
    assert call["statement"] == (
        "RSI effect persists across markets."
    )
    assert call["applicability"] == (
        "liquid FX",
    )
    assert payload["artifact_version"] == 2
    assert payload["knowledge_revision"][
        "item"
    ]["id"] == "knowledge-rsi"
    assert payload["knowledge_revision"][
        "fingerprint"
    ] == promotion_application.result.fingerprint


def test_rejects_unconfigured_requested_promotion(
) -> None:
    loaded_request = StubLoadedRequest(
        hypothesis_id="hypothesis-rsi",
        requests=("request-a",),
        knowledge_promotion=(
            KnowledgePromotionRequest(
                knowledge_id="knowledge-rsi",
                statement="RSI effect persists.",
                applicability=("liquid FX",),
                limitations=(),
                provenance=(
                    ("producer", "request"),
                ),
            )
        ),
    )
    command = (
        RunIndicatorComparativeHypothesisEvaluationCommand(
            application=StubApplication(
                build_evaluation()
            ),
            request_loader=StubRequestLoader(
                loaded_request
            ),
        )
    )

    with pytest.raises(
        ValueError,
        match=(
            "Knowledge promotion is not configured"
        ),
    ):
        command.execute(
            "evaluation-request.json"
        )
