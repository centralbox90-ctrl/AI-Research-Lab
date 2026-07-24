import json
from pathlib import Path

import pytest

from src.application.campaign_design_loader import (
    CampaignDesignLoader,
)
from src.research.campaign_design import (
    CampaignDesign,
)


def build_payload() -> dict[str, object]:
    return {
        "schema_version": 1,
        "question_id": " question-rsi ",
        "hypothesis_ids": [
            "hypothesis-b",
            "hypothesis-a",
        ],
        "instruments": [
            "EURUSD",
            "BTCUSDT",
        ],
        "timeframes": [
            "H4",
            "H1",
        ],
        "data_periods": [
            "training-period-v1",
        ],
        "indicator_configurations": [
            "rsi-period-14",
        ],
        "signal_rules": [
            "rsi-oversold-entry-v1",
        ],
        "execution_policies": [
            "long-stop-take-v1",
        ],
        "baselines": [
            "unconditional-return-v1",
        ],
        "validation_strategy": " walk-forward-v1 ",
        "evaluation_plan_ref": " comparative-plan-v1 ",
        "provenance": {
            "question_fingerprint": (
                "question-fingerprint"
            ),
            "design_source": "campaign-json-v1",
        },
    }


def test_loads_normalized_campaign_design() -> None:
    design = CampaignDesignLoader().from_dict(
        build_payload()
    )

    assert isinstance(design, CampaignDesign)
    assert design.question_id == "question-rsi"
    assert design.hypothesis_ids == (
        "hypothesis-a",
        "hypothesis-b",
    )
    assert design.instruments == (
        "BTCUSDT",
        "EURUSD",
    )
    assert design.timeframes == (
        "H1",
        "H4",
    )
    assert design.validation_strategy == (
        "walk-forward-v1"
    )
    assert design.evaluation_plan_ref == (
        "comparative-plan-v1"
    )


def test_loads_serialized_campaign_design() -> None:
    first = CampaignDesignLoader().from_dict(
        build_payload()
    )

    second = CampaignDesignLoader().from_dict(
        first.to_dict()
    )

    assert second == first
    assert second.id == first.id
    assert second.fingerprint == first.fingerprint


def test_loads_utf8_json_file(
    tmp_path: Path,
) -> None:
    payload = build_payload()
    payload["question_id"] = (
        "вопрос-перепроданность-rsi"
    )
    design_path = tmp_path / "campaign-design.json"
    design_path.write_text(
        json.dumps(
            payload,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    design = CampaignDesignLoader().load(
        design_path
    )

    assert design.question_id == (
        "вопрос-перепроданность-rsi"
    )


def test_rejects_invalid_json_file(
    tmp_path: Path,
) -> None:
    design_path = tmp_path / "campaign-design.json"
    design_path.write_text(
        "{invalid-json",
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="invalid campaign design JSON",
    ):
        CampaignDesignLoader().load(design_path)


def test_rejects_non_object_payload() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "campaign design JSON must contain an object"
        ),
    ):
        CampaignDesignLoader().from_dict([])


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
    payload = build_payload()
    payload["schema_version"] = schema_version

    with pytest.raises(
        ValueError,
        match="schema_version must be 1",
    ):
        CampaignDesignLoader().from_dict(payload)


def test_rejects_missing_field() -> None:
    payload = build_payload()
    del payload["question_id"]

    with pytest.raises(
        ValueError,
        match=(
            "missing campaign design fields: question_id"
        ),
    ):
        CampaignDesignLoader().from_dict(payload)


def test_rejects_unknown_field() -> None:
    payload = build_payload()
    payload["python_factory"] = "package.module:factory"

    with pytest.raises(
        ValueError,
        match=(
            "unknown campaign design fields: "
            "python_factory"
        ),
    ):
        CampaignDesignLoader().from_dict(payload)


@pytest.mark.parametrize(
    "field_name",
    (
        "hypothesis_ids",
        "instruments",
        "timeframes",
        "data_periods",
        "indicator_configurations",
        "signal_rules",
        "execution_policies",
        "baselines",
    ),
)
def test_requires_array_dimensions(
    field_name: str,
) -> None:
    payload = build_payload()
    payload[field_name] = "not-an-array"

    with pytest.raises(
        ValueError,
        match=f"{field_name} must be an array",
    ):
        CampaignDesignLoader().from_dict(payload)


def test_requires_provenance_object() -> None:
    payload = build_payload()
    payload["provenance"] = [
        "design_source",
        "campaign-json-v1",
    ]

    with pytest.raises(
        ValueError,
        match="provenance must be an object",
    ):
        CampaignDesignLoader().from_dict(payload)


def test_rejects_mismatched_supplied_id() -> None:
    payload = build_payload()
    payload["id"] = "campaign-design:sha256:other"

    with pytest.raises(
        ValueError,
        match=(
            "id must match the computed campaign design ID"
        ),
    ):
        CampaignDesignLoader().from_dict(payload)


def test_rejects_invalid_supplied_id() -> None:
    payload = build_payload()
    payload["id"] = " "

    with pytest.raises(
        ValueError,
        match="id must be a non-empty string",
    ):
        CampaignDesignLoader().from_dict(payload)


def test_delegates_dimension_validation() -> None:
    payload = build_payload()
    payload["timeframes"] = [
        "H1",
        "H1",
    ]

    with pytest.raises(
        ValueError,
        match=(
            "timeframes must not contain duplicates"
        ),
    ):
        CampaignDesignLoader().from_dict(payload)


def test_delegates_provenance_validation() -> None:
    payload = build_payload()
    payload["provenance"] = {
        "design_source": " ",
    }

    with pytest.raises(
        ValueError,
        match="provenance value must not be empty",
    ):
        CampaignDesignLoader().from_dict(payload)
