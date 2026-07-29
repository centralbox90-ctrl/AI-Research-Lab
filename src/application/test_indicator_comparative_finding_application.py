from __future__ import annotations

import pytest

from src.application.indicator_comparative_evidence_application import (
    IndicatorComparativeEvidenceApplication,
)
from src.application.indicator_comparative_finding_application import (
    IndicatorComparativeFindingApplication,
)
from src.research.evidence import (
    Evidence,
    EvidenceDirection,
    EvidenceStrength,
)
from src.research.finding import (
    Finding,
    FindingRelationship,
)
from src.research.finding_evaluator import (
    FindingEvaluator,
)
from src.research.outcome_specification import (
    ForwardReturnSpecification,
)


def build_evidence() -> Evidence:
    return Evidence(
        id="evidence:sha256:example",
        hypothesis_id="hypothesis-rsi",
        observation_refs=(
            "dataset-a:horizon:3",
            "dataset-b:horizon:3",
        ),
        direction=EvidenceDirection.SUPPORTING,
        strength=EvidenceStrength.STRONG,
        confidence=0.95,
        consistency=1.0,
        robustness=1.0,
        provenance=(
            ("method", "moving_block_bootstrap"),
            ("research_fingerprint", "research-1"),
        ),
        applicability=(
            "indicator:rsi",
            "symbol:EURUSD",
            "timeframe:H1",
            "horizon:3",
        ),
        limitations=(
            "historical datasets only",
        ),
    )


class StubEvidenceApplication(
    IndicatorComparativeEvidenceApplication
):
    def __init__(
        self,
        result: object,
    ) -> None:
        self.result = result
        self.calls: list[
            dict[str, object]
        ] = []

    def run(
        self,
        **arguments: object,
    ) -> Evidence:
        self.calls.append(dict(arguments))

        return self.result  # type: ignore[return-value]


def build_application(
    result: object | None = None,
) -> tuple[
    IndicatorComparativeFindingApplication,
    StubEvidenceApplication,
]:
    evidence_application = StubEvidenceApplication(
        build_evidence()
        if result is None
        else result
    )
    application = (
        IndicatorComparativeFindingApplication(
            evidence_application=(
                evidence_application
            ),
            finding_evaluator=FindingEvaluator(),
        )
    )

    return application, evidence_application


def test_runs_evidence_application_into_finding(
) -> None:
    application, evidence_application = (
        build_application()
    )
    market_specifications = (
        object(),
        object(),
    )
    outcome_specification = (
        ForwardReturnSpecification(
            horizons=(1, 3),
        )
    )

    finding = application.run(
        hypothesis_id="hypothesis-rsi",
        market_specifications=(  # type: ignore[arg-type]
            market_specifications
        ),
        indicator_id="rsi",
        outcome_specification=(
            outcome_specification
        ),
        horizon=3,
        statement=(
            "RSI improves entries on EURUSD H1."
        ),
        applicable_markets=(
            "EURUSD:H1",
        ),
        correlation_id="research-lifecycle-42",
        analysis_pipeline_version="analysis-v1",
    )

    assert isinstance(finding, Finding)
    assert finding.relationship is (
        FindingRelationship.SUPPORTING
    )
    assert finding.hypothesis_id == (
        "hypothesis-rsi"
    )
    assert finding.statement == (
        "RSI improves entries on EURUSD H1."
    )
    assert finding.applicable_markets == (
        "EURUSD:H1",
    )
    assert finding.supporting_evidence == (
        "evidence:sha256:example",
    )
    assert len(evidence_application.calls) == 1
    assert evidence_application.calls[0] == {
        "hypothesis_id": "hypothesis-rsi",
        "market_specifications": (
            market_specifications
        ),
        "indicator_id": "rsi",
        "outcome_specification": (
            outcome_specification
        ),
        "horizon": 3,
        "correlation_id": (
            "research-lifecycle-42"
        ),
    }
    assert dict(finding.provenance)[
        "analysis_pipeline_version"
    ] == "analysis-v1"


@pytest.mark.parametrize(
    "invalid_dependency",
    (
        "evidence_application",
        "finding_evaluator",
    ),
)
def test_rejects_invalid_dependency(
    invalid_dependency: str,
) -> None:
    arguments: dict[str, object] = {
        "evidence_application": (
            StubEvidenceApplication(
                build_evidence()
            )
        ),
        "finding_evaluator": FindingEvaluator(),
    }
    arguments[invalid_dependency] = object()

    with pytest.raises(
        TypeError,
        match=(
            "evidence_application must be an "
            "IndicatorComparativeEvidenceApplication"
            if invalid_dependency
            == "evidence_application"
            else (
                "finding_evaluator must be a "
                "FindingEvaluator"
            )
        ),
    ):
        IndicatorComparativeFindingApplication(
            **arguments,  # type: ignore[arg-type]
        )


def test_rejects_invalid_evidence_result() -> None:
    application, _ = build_application(
        result=object()
    )

    with pytest.raises(
        TypeError,
        match="evidence must be an Evidence",
    ):
        application.run(
            hypothesis_id="hypothesis-rsi",
            market_specifications=(),  # type: ignore[arg-type]
            indicator_id="rsi",
            outcome_specification=(
                ForwardReturnSpecification(
                    horizons=(3,),
                )
            ),
            horizon=3,
            statement="Statement.",
            applicable_markets=(
                "EURUSD:H1",
            ),
        )


def test_uses_default_pipeline_version() -> None:
    application, _ = build_application()

    finding = application.run(
        hypothesis_id="hypothesis-rsi",
        market_specifications=(),  # type: ignore[arg-type]
        indicator_id="rsi",
        outcome_specification=(
            ForwardReturnSpecification(
                horizons=(3,),
            )
        ),
        horizon=3,
        statement="Statement.",
        applicable_markets=(
            "EURUSD:H1",
        ),
    )

    assert dict(finding.provenance)[
        "analysis_pipeline_version"
    ] == FindingEvaluator.DEFAULT_PIPELINE_VERSION