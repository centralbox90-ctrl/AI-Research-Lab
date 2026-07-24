import json
from pathlib import Path

import pytest

from src.application.in_memory_market_experiment_specification_resolver import (
    InMemoryMarketExperimentSpecificationResolver,
)
from src.application.market_experiment_registration_loader import (
    MarketExperimentRegistrationLoader,
)
from src.research.campaign_design import CampaignDesign
from src.research.research_planner import (
    CampaignExperimentSpecification,
    ResearchCampaignPlan,
    ResearchPlanner,
)


def build_plan() -> ResearchCampaignPlan:
    design = CampaignDesign(
        question_id="question-rsi",
        hypothesis_ids=("hypothesis-rsi",),
        instruments=(
            "BTCUSDT",
            "EURUSD",
        ),
        timeframes=("H1",),
        data_periods=("training-period-v1",),
        indicator_configurations=("rsi-period-14",),
        signal_rules=("rsi-oversold-entry-v1",),
        execution_policies=("long-stop-take-v1",),
        baselines=("unconditional-return-v1",),
        validation_strategy="walk-forward-v1",
        evaluation_plan_ref="comparative-plan-v1",
        provenance=(
            (
                "question_fingerprint",
                "question-fingerprint",
            ),
        ),
    )

    return ResearchPlanner().plan(design)


def build_market_payload(
    planned_specification: CampaignExperimentSpecification,
) -> dict[str, object]:
    return {
        "executor_type": "market_backtest",
        "question_title": (
            "Does RSI oversold predict positive returns?"
        ),
        "question_description": (
            "Evaluate an RSI oversold signal "
            "on historical data."
        ),
        "hypothesis_title": (
            "RSI oversold values precede positive returns"
        ),
        "hypothesis_description": (
            "The registered RSI signal should "
            "produce positive historical returns."
        ),
        "expected_result": (
            "Positive net profit with a non-zero trade count."
        ),
        "experiment_title": (
            f"{planned_specification.instrument} "
            f"{planned_specification.timeframe} RSI backtest"
        ),
        "experiment_description": (
            "Execute one registered campaign experiment."
        ),
        "data_source": "historical_csv",
        "symbol": planned_specification.instrument,
        "timeframe": planned_specification.timeframe,
        "start_at": "2024-01-01T00:00:00Z",
        "end_at": "2024-12-31T00:00:00Z",
        "entry_rule": "rsi-oversold-entry-v1",
        "exit_rule": "stop-take-or-max-holding-v1",
        "direction": "LONG",
        "stop_loss_percent": 1.0,
        "take_profit_percent": 2.0,
        "max_holding_bars": 24,
        "commission_percent": 0.1,
        "slippage_percent": 0.05,
        "strategy_parameters": {
            "rsi_period": 14,
            "oversold_level": 30,
        },
        "tags": [
            planned_specification.campaign_design_id,
            planned_specification.id,
        ],
    }


def build_payload(
    plan: ResearchCampaignPlan,
) -> dict[str, object]:
    return {
        "schema_version": 1,
        "campaign_plan_id": plan.id,
        "registrations": [
            {
                "planned_experiment_id": (
                    planned_specification.id
                ),
                "market_specification": (
                    build_market_payload(
                        planned_specification
                    )
                ),
            }
            for planned_specification
            in plan.experiment_specifications
        ],
    }


def test_loads_complete_registration_set() -> None:
    plan = build_plan()

    resolver = (
        MarketExperimentRegistrationLoader().from_dict(
            build_payload(plan),
            plan=plan,
        )
    )

    assert isinstance(
        resolver,
        InMemoryMarketExperimentSpecificationResolver,
    )
    assert resolver.registered_ids == tuple(
        sorted(plan.experiment_ids)
    )

    for planned_specification in (
        plan.experiment_specifications
    ):
        resolved = resolver.resolve(
            planned_specification
        )
        assert (
            resolved.symbol
            == planned_specification.instrument
        )
        assert (
            resolved.timeframe
            == planned_specification.timeframe
        )


def test_loads_utf8_json_file(
    tmp_path: Path,
) -> None:
    plan = build_plan()
    payload = build_payload(plan)
    payload["registrations"][0][
        "market_specification"
    ]["question_title"] = (
        "Предсказывает ли перепроданность рост?"
    )

    registration_path = (
        tmp_path / "campaign-registrations.json"
    )
    registration_path.write_text(
        json.dumps(
            payload,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    resolver = MarketExperimentRegistrationLoader().load(
        registration_path,
        plan=plan,
    )

    first = plan.experiment_specifications[0]

    assert (
        resolver.resolve(first).question_title
        == "Предсказывает ли перепроданность рост?"
    )


def test_rejects_invalid_json_file(
    tmp_path: Path,
) -> None:
    plan = build_plan()
    registration_path = (
        tmp_path / "campaign-registrations.json"
    )
    registration_path.write_text(
        "{invalid-json",
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="invalid campaign registration JSON",
    ):
        MarketExperimentRegistrationLoader().load(
            registration_path,
            plan=plan,
        )


def test_rejects_non_object_payload() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "campaign registration JSON "
            "must contain an object"
        ),
    ):
        MarketExperimentRegistrationLoader().from_dict(
            [],
            plan=build_plan(),
        )


def test_rejects_invalid_plan() -> None:
    with pytest.raises(
        TypeError,
        match="plan must be a ResearchCampaignPlan",
    ):
        MarketExperimentRegistrationLoader().from_dict(
            {},
            plan=object(),
        )


@pytest.mark.parametrize(
    "schema_version",
    (
        2,
        True,
        "1",
    ),
)
def test_rejects_unsupported_schema_version(
    schema_version: object,
) -> None:
    plan = build_plan()
    payload = build_payload(plan)
    payload["schema_version"] = schema_version

    with pytest.raises(
        ValueError,
        match="schema_version must be 1",
    ):
        MarketExperimentRegistrationLoader().from_dict(
            payload,
            plan=plan,
        )


def test_rejects_different_campaign_plan() -> None:
    plan = build_plan()
    payload = build_payload(plan)
    payload["campaign_plan_id"] = (
        "research-campaign-plan:sha256:other"
    )

    with pytest.raises(
        ValueError,
        match=(
            "campaign_plan_id must match "
            "the supplied research plan"
        ),
    ):
        MarketExperimentRegistrationLoader().from_dict(
            payload,
            plan=plan,
        )


def test_rejects_missing_registration() -> None:
    plan = build_plan()
    payload = build_payload(plan)
    payload["registrations"].pop()

    with pytest.raises(
        ValueError,
        match=(
            "missing planned experiment registrations"
        ),
    ):
        MarketExperimentRegistrationLoader().from_dict(
            payload,
            plan=plan,
        )


def test_rejects_duplicate_registration() -> None:
    plan = build_plan()
    payload = build_payload(plan)
    payload["registrations"].append(
        dict(payload["registrations"][0])
    )

    with pytest.raises(
        ValueError,
        match=(
            "planned_experiment_id values "
            "must be unique"
        ),
    ):
        MarketExperimentRegistrationLoader().from_dict(
            payload,
            plan=plan,
        )


def test_rejects_unknown_planned_experiment() -> None:
    plan = build_plan()
    payload = build_payload(plan)
    payload["registrations"][0][
        "planned_experiment_id"
    ] = "campaign-experiment-specification:unknown"

    with pytest.raises(
        ValueError,
        match=(
            "registration references an unknown "
            "planned experiment"
        ),
    ):
        MarketExperimentRegistrationLoader().from_dict(
            payload,
            plan=plan,
        )


def test_rejects_mismatched_symbol() -> None:
    plan = build_plan()
    payload = build_payload(plan)
    payload["registrations"][0][
        "market_specification"
    ]["symbol"] = "XAUUSD"

    with pytest.raises(
        ValueError,
        match=(
            "symbol must match the planned instrument"
        ),
    ):
        MarketExperimentRegistrationLoader().from_dict(
            payload,
            plan=plan,
        )


def test_rejects_mismatched_timeframe() -> None:
    plan = build_plan()
    payload = build_payload(plan)
    payload["registrations"][0][
        "market_specification"
    ]["timeframe"] = "D1"

    with pytest.raises(
        ValueError,
        match=(
            "timeframe must match the planned timeframe"
        ),
    ):
        MarketExperimentRegistrationLoader().from_dict(
            payload,
            plan=plan,
        )


def test_rejects_unknown_top_level_field() -> None:
    plan = build_plan()
    payload = build_payload(plan)
    payload["python_factory"] = "package.module:factory"

    with pytest.raises(
        ValueError,
        match=(
            "unknown campaign registration fields: "
            "python_factory"
        ),
    ):
        MarketExperimentRegistrationLoader().from_dict(
            payload,
            plan=plan,
        )


def test_rejects_invalid_registration_entry() -> None:
    plan = build_plan()
    payload = build_payload(plan)
    payload["registrations"][0] = "invalid"

    with pytest.raises(
        ValueError,
        match="registration 0 must be an object",
    ):
        MarketExperimentRegistrationLoader().from_dict(
            payload,
            plan=plan,
        )


def test_delegates_market_specification_validation() -> None:
    plan = build_plan()
    payload = build_payload(plan)
    del payload["registrations"][0][
        "market_specification"
    ]["data_source"]

    with pytest.raises(
        ValueError,
        match=(
            "missing specification fields: data_source"
        ),
    ):
        MarketExperimentRegistrationLoader().from_dict(
            payload,
            plan=plan,
        )
