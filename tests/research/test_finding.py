from dataclasses import FrozenInstanceError

import pytest

from src.research.finding import (
    Finding,
    FindingRelationship,
)


def build_finding(
    **overrides: object,
) -> Finding:
    values: dict[str, object] = {
        "id": "finding-rsi",
        "hypothesis_id": "hypothesis-rsi",
        "statement": (
            "RSI improves entries in selected markets."
        ),
        "relationship": (
            FindingRelationship.SUPPORTING
        ),
        "confidence": 0.8,
        "applicable_markets": (
            "EURUSD:H1",
            "GBPUSD:H1",
        ),
        "limitations": (
            "high-volatility periods only",
        ),
        "supporting_evidence": (
            "evidence-b",
            "evidence-a",
        ),
        "provenance": (
            ("pipeline_version", "analysis-v1"),
            ("method", "moving_block_bootstrap"),
        ),
    }
    values.update(overrides)

    return Finding(**values)  # type: ignore[arg-type]


def test_normalizes_finding() -> None:
    finding = build_finding(
        id="  finding-rsi  ",
        hypothesis_id="  hypothesis-rsi  ",
        statement="  Supported statement.  ",
        applicable_markets=(
            "  GBPUSD:H1  ",
            "EURUSD:H1",
        ),
        limitations=(
            "  limited period  ",
        ),
        supporting_evidence=(
            "evidence-b",
            "  evidence-a  ",
        ),
        provenance=(
            ("  method  ", "  bootstrap  "),
            ("pipeline", "analysis-v1"),
        ),
    )

    assert finding.id == "finding-rsi"
    assert finding.hypothesis_id == "hypothesis-rsi"
    assert finding.statement == "Supported statement."
    assert finding.relationship is (
        FindingRelationship.SUPPORTING
    )
    assert finding.applicable_markets == (
        "EURUSD:H1",
        "GBPUSD:H1",
    )
    assert finding.limitations == (
        "limited period",
    )
    assert finding.supporting_evidence == (
        "evidence-a",
        "evidence-b",
    )
    assert finding.provenance == (
        ("method", "bootstrap"),
        ("pipeline", "analysis-v1"),
    )


def test_serializes_public_contract() -> None:
    finding = build_finding()

    assert finding.to_dict() == {
        "schema_version": 2,
        "id": "finding-rsi",
        "hypothesis_id": "hypothesis-rsi",
        "statement": (
            "RSI improves entries in selected markets."
        ),
        "relationship": "supporting",
        "confidence": 0.8,
        "applicable_markets": [
            "EURUSD:H1",
            "GBPUSD:H1",
        ],
        "limitations": [
            "high-volatility periods only",
        ],
        "supporting_evidence": [
            "evidence-a",
            "evidence-b",
        ],
        "provenance": {
            "method": "moving_block_bootstrap",
            "pipeline_version": "analysis-v1",
        },
    }


def test_fingerprint_is_order_independent() -> None:
    first = build_finding()
    second = build_finding(
        applicable_markets=(
            "GBPUSD:H1",
            "EURUSD:H1",
        ),
        supporting_evidence=(
            "evidence-a",
            "evidence-b",
        ),
        provenance=(
            ("method", "moving_block_bootstrap"),
            ("pipeline_version", "analysis-v1"),
        ),
    )

    assert first == second
    assert first.fingerprint == second.fingerprint
    assert len(first.fingerprint) == 64


def test_is_immutable() -> None:
    finding = build_finding()

    with pytest.raises(FrozenInstanceError):
        finding.statement = "changed"  # type: ignore[misc]


@pytest.mark.parametrize(
    ("field_name", "value", "error_type", "message"),
    (
        ("id", object(), TypeError, "id must be a string"),
        ("id", " ", ValueError, "id must not be empty"),
        (
            "hypothesis_id",
            object(),
            TypeError,
            "hypothesis_id must be a string",
        ),
        (
            "hypothesis_id",
            " ",
            ValueError,
            "hypothesis_id must not be empty",
        ),
        (
            "statement",
            object(),
            TypeError,
            "statement must be a string",
        ),
        (
            "statement",
            " ",
            ValueError,
            "statement must not be empty",
        ),
    ),
)
def test_rejects_invalid_required_text(
    field_name: str,
    value: object,
    error_type: type[Exception],
    message: str,
) -> None:
    with pytest.raises(error_type, match=message):
        build_finding(**{field_name: value})


def test_rejects_invalid_relationship() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "relationship must be a "
            "FindingRelationship"
        ),
    ):
        build_finding(
            relationship="supporting",
        )


@pytest.mark.parametrize(
    ("value", "error_type", "message"),
    (
        (
            True,
            TypeError,
            "confidence must be a real number",
        ),
        (
            float("nan"),
            ValueError,
            "confidence must be finite",
        ),
        (
            -0.1,
            ValueError,
            "confidence must be between 0 and 1",
        ),
        (
            1.1,
            ValueError,
            "confidence must be between 0 and 1",
        ),
    ),
)
def test_rejects_invalid_confidence(
    value: object,
    error_type: type[Exception],
    message: str,
) -> None:
    with pytest.raises(error_type, match=message):
        build_finding(confidence=value)


@pytest.mark.parametrize(
    ("field_name", "value", "error_type", "message"),
    (
        (
            "applicable_markets",
            [],
            TypeError,
            "applicable_markets must be a tuple",
        ),
        (
            "applicable_markets",
            (),
            ValueError,
            "applicable_markets must not be empty",
        ),
        (
            "applicable_markets",
            ("EURUSD:H1", " EURUSD:H1 "),
            ValueError,
            "applicable_markets must not contain duplicates",
        ),
        (
            "supporting_evidence",
            (),
            ValueError,
            "supporting_evidence must not be empty",
        ),
        (
            "limitations",
            ("same", " same "),
            ValueError,
            "limitations must not contain duplicates",
        ),
    ),
)
def test_rejects_invalid_text_collections(
    field_name: str,
    value: object,
    error_type: type[Exception],
    message: str,
) -> None:
    with pytest.raises(error_type, match=message):
        build_finding(**{field_name: value})


@pytest.mark.parametrize(
    ("value", "error_type", "message"),
    (
        (
            [],
            TypeError,
            "provenance must be a tuple",
        ),
        (
            (),
            ValueError,
            "provenance must not be empty",
        ),
        (
            (("method",),),
            TypeError,
            "each provenance entry must be a key-value tuple",
        ),
        (
            (("method", "a"), (" method ", "b")),
            ValueError,
            "provenance keys must be unique",
        ),
    ),
)
def test_rejects_invalid_provenance(
    value: object,
    error_type: type[Exception],
    message: str,
) -> None:
    with pytest.raises(error_type, match=message):
        build_finding(provenance=value)