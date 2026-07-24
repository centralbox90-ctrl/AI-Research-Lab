from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import pytest

from src.application.indicator_comparative_hypothesis_evaluation_application import (
    IndicatorComparativeHypothesisEvaluationApplication,
)
from src.application.indicator_comparative_hypothesis_evaluation_request_loader import (
    IndicatorComparativeHypothesisEvaluationRequestLoader,
)
from src.cli.run_indicator_comparative_hypothesis_evaluation_command import (
    RunIndicatorComparativeHypothesisEvaluationCommand,
)
from src.research.hypothesis_evaluation import (
    HypothesisEvaluation,
    HypothesisEvaluationState,
)


@dataclass(frozen=True)
class StubLoadedRequest:
    hypothesis_id: str
    requests: tuple[object, ...]


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