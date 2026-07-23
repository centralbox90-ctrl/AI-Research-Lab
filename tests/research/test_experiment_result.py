from dataclasses import FrozenInstanceError
from datetime import UTC, datetime

import pandas as pd
import pytest

from src.research.comparative_analysis_service import (
    ComparativeAnalysisService,
)
from src.research.experiment_result import (
    ExperimentResult,
)
from src.research.observations.observation import (
    Observation,
)
from src.research.outcome_specification import (
    ForwardReturnSpecification,
)


def build_analysis():
    data = pd.DataFrame(
        {
            "close": [
                100.0,
                110.0,
                120.0,
            ],
        }
    )
    observation = Observation(
        id="observation",
        definition_id="definition",
        symbol="EURUSD",
        timeframe="H1",
        timestamp=datetime(
            2026,
            1,
            1,
            tzinfo=UTC,
        ),
        bar_index=0,
        price=100.0,
    )

    return ComparativeAnalysisService().run(
        data=data,
        observations=(observation,),
        specification=(
            ForwardReturnSpecification(
                horizons=(1,),
            )
        ),
    )


def build_result(
    **changes: object,
) -> ExperimentResult:
    values = {
        "id": "result-1",
        "experiment_id": "experiment-1",
        "analysis": build_analysis(),
        "created_at": datetime(
            2026,
            7,
            23,
            12,
            0,
            tzinfo=UTC,
        ),
        "provenance": (
            ("dataset_snapshot", "dataset-1"),
            ("code_revision", "abc123"),
        ),
    }
    values.update(changes)

    return ExperimentResult(**values)


def test_stores_reproducible_result() -> None:
    result = build_result(
        id="  result-1  ",
        experiment_id="  experiment-1  ",
        provenance=(
            (
                "  dataset_snapshot  ",
                "  dataset-1  ",
            ),
        ),
    )

    assert result.id == "result-1"
    assert result.experiment_id == "experiment-1"
    assert result.provenance == (
        ("dataset_snapshot", "dataset-1"),
    )
    assert result.analysis.comparisons


def test_is_immutable() -> None:
    result = build_result()

    with pytest.raises(FrozenInstanceError):
        result.experiment_id = "changed"


@pytest.mark.parametrize(
    "field_name",
    (
        "id",
        "experiment_id",
    ),
)
def test_rejects_non_string_identifiers(
    field_name: str,
) -> None:
    with pytest.raises(
        TypeError,
        match=f"{field_name} must be a string",
    ):
        build_result(
            **{field_name: object()}
        )


@pytest.mark.parametrize(
    "field_name",
    (
        "id",
        "experiment_id",
    ),
)
def test_rejects_empty_identifiers(
    field_name: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=f"{field_name} must not be empty",
    ):
        build_result(
            **{field_name: "   "}
        )


def test_rejects_invalid_analysis() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "analysis must be a "
            "ComparativeAnalysis"
        ),
    ):
        build_result(
            analysis=object()
        )


def test_rejects_invalid_created_at() -> None:
    with pytest.raises(
        TypeError,
        match="created_at must be a datetime",
    ):
        build_result(
            created_at=object()
        )


def test_rejects_naive_created_at() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "created_at must be timezone-aware"
        ),
    ):
        build_result(
            created_at=datetime(
                2026,
                7,
                23,
            )
        )


def test_rejects_non_tuple_provenance() -> None:
    with pytest.raises(
        TypeError,
        match="provenance must be a tuple",
    ):
        build_result(
            provenance=[]
        )


@pytest.mark.parametrize(
    "invalid_value",
    (
        "dataset-1",
        ("dataset",),
        ("dataset", "one", "extra"),
    ),
)
def test_rejects_invalid_provenance_entry(
    invalid_value: object,
) -> None:
    with pytest.raises(
        TypeError,
        match=(
            "each provenance value must be "
            "a key-value tuple"
        ),
    ):
        build_result(
            provenance=(invalid_value,)
        )


def test_rejects_duplicate_provenance_keys(
) -> None:
    with pytest.raises(
        ValueError,
        match="provenance keys must be unique",
    ):
        build_result(
            provenance=(
                ("dataset", "one"),
                ("dataset", "two"),
            )
        )
