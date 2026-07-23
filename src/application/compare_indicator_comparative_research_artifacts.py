from __future__ import annotations

from math import isfinite
from numbers import Real
from typing import Any


class CompareIndicatorComparativeResearchArtifacts:
    """
    Compares horizon effects from two indicator research artifacts.

    File loading and presentation remain outside this service.
    """

    _METRIC_FIELDS = (
        "mean_return_difference",
        "median_return_difference",
        "positive_rate_difference",
    )

    def execute(
        self,
        artifact_a: dict[str, Any],
        artifact_b: dict[str, Any],
    ) -> dict[str, Any]:
        identity_a = self._extract_identity(
            artifact_a,
            artifact_label="artifact_a",
        )
        identity_b = self._extract_identity(
            artifact_b,
            artifact_label="artifact_b",
        )

        self._validate_compatible_identity(
            identity_a,
            identity_b,
        )

        comparisons_a = self._index_comparisons(
            artifact_a,
            artifact_label="artifact_a",
        )
        comparisons_b = self._index_comparisons(
            artifact_b,
            artifact_label="artifact_b",
        )

        horizons_a = set(comparisons_a)
        horizons_b = set(comparisons_b)

        if horizons_a != horizons_b:
            raise ValueError(
                "artifacts must have the same "
                "comparison horizons"
            )

        horizons = sorted(horizons_a)

        return {
            "artifact_type": (
                "indicator_comparative_research_comparison"
            ),
            "artifact_version": 1,
            "artifact_a": {
                "research_fingerprint": identity_a[
                    "research_fingerprint"
                ],
                "dataset_id": identity_a[
                    "dataset_id"
                ],
            },
            "artifact_b": {
                "research_fingerprint": identity_b[
                    "research_fingerprint"
                ],
                "dataset_id": identity_b[
                    "dataset_id"
                ],
            },
            "indicator": {
                "id": identity_a["indicator_id"],
            },
            "market": {
                "symbol": identity_a["symbol"],
                "timeframe": identity_a["timeframe"],
            },
            "outcome_specification": {
                "horizons": horizons,
                "price_field": identity_a[
                    "price_field"
                ],
            },
            "horizon_deltas": [
                self._build_horizon_delta(
                    horizon=horizon,
                    comparison_a=(
                        comparisons_a[horizon]
                    ),
                    comparison_b=(
                        comparisons_b[horizon]
                    ),
                )
                for horizon in horizons
            ],
        }

    def _extract_identity(
        self,
        artifact: dict[str, Any],
        *,
        artifact_label: str,
    ) -> dict[str, str]:
        if not isinstance(artifact, dict):
            raise TypeError(
                f"{artifact_label} must be a dictionary"
            )

        indicator = self._require_mapping(
            artifact,
            "indicator",
            parent_name=artifact_label,
        )
        market = self._require_mapping(
            artifact,
            "market",
            parent_name=artifact_label,
        )
        dataset = self._require_mapping(
            artifact,
            "dataset",
            parent_name=artifact_label,
        )
        outcome_specification = (
            self._require_mapping(
                artifact,
                "outcome_specification",
                parent_name=artifact_label,
            )
        )

        return {
            "indicator_id": self._require_text(
                indicator,
                "id",
                parent_name=(
                    f"{artifact_label}.indicator"
                ),
            ),
            "research_fingerprint": (
                self._require_text(
                    indicator,
                    "research_fingerprint",
                    parent_name=(
                        f"{artifact_label}.indicator"
                    ),
                )
            ),
            "dataset_id": self._require_text(
                dataset,
                "id",
                parent_name=(
                    f"{artifact_label}.dataset"
                ),
            ),
            "symbol": self._require_text(
                market,
                "symbol",
                parent_name=(
                    f"{artifact_label}.market"
                ),
            ),
            "timeframe": self._require_text(
                market,
                "timeframe",
                parent_name=(
                    f"{artifact_label}.market"
                ),
            ),
            "price_field": self._require_text(
                outcome_specification,
                "price_field",
                parent_name=(
                    f"{artifact_label}."
                    "outcome_specification"
                ),
            ),
        }

    @staticmethod
    def _validate_compatible_identity(
        identity_a: dict[str, str],
        identity_b: dict[str, str],
    ) -> None:
        compatible_fields = {
            "indicator_id": "indicator id",
            "symbol": "symbol",
            "timeframe": "timeframe",
            "price_field": "price field",
        }

        for field_name, description in (
            compatible_fields.items()
        ):
            if (
                identity_a[field_name]
                != identity_b[field_name]
            ):
                raise ValueError(
                    "artifacts must have the same "
                    f"{description}"
                )

    def _index_comparisons(
        self,
        artifact: dict[str, Any],
        *,
        artifact_label: str,
    ) -> dict[int, dict[str, float]]:
        analysis = self._require_mapping(
            artifact,
            "analysis",
            parent_name=artifact_label,
        )
        comparisons = analysis.get(
            "comparisons"
        )

        if not isinstance(comparisons, list):
            raise ValueError(
                f"{artifact_label}.analysis.comparisons "
                "must be an array"
            )

        indexed: dict[int, dict[str, float]] = {}

        for position, comparison in enumerate(
            comparisons
        ):
            comparison_name = (
                f"{artifact_label}.analysis."
                f"comparisons[{position}]"
            )

            if not isinstance(comparison, dict):
                raise ValueError(
                    f"{comparison_name} must be an object"
                )

            horizon = self._require_positive_integer(
                comparison,
                "horizon",
                parent_name=comparison_name,
            )

            if horizon in indexed:
                raise ValueError(
                    f"{artifact_label} contains duplicate "
                    f"comparison horizon {horizon}"
                )

            indexed[horizon] = {
                metric_name: self._require_number(
                    comparison,
                    metric_name,
                    parent_name=comparison_name,
                )
                for metric_name in self._METRIC_FIELDS
            }

        return indexed

    def _build_horizon_delta(
        self,
        *,
        horizon: int,
        comparison_a: dict[str, float],
        comparison_b: dict[str, float],
    ) -> dict[str, int | float]:
        return {
            "horizon": horizon,
            **{
                f"{metric_name}_delta": (
                    comparison_b[metric_name]
                    - comparison_a[metric_name]
                )
                for metric_name in self._METRIC_FIELDS
            },
        }

    @staticmethod
    def _require_mapping(
        container: dict[str, Any],
        field_name: str,
        *,
        parent_name: str,
    ) -> dict[str, Any]:
        value = container.get(field_name)

        if not isinstance(value, dict):
            raise ValueError(
                f"{parent_name}.{field_name} "
                "must be an object"
            )

        return value

    @staticmethod
    def _require_text(
        container: dict[str, Any],
        field_name: str,
        *,
        parent_name: str,
    ) -> str:
        value = container.get(field_name)

        if (
            not isinstance(value, str)
            or not value.strip()
        ):
            raise ValueError(
                f"{parent_name}.{field_name} "
                "must be a non-empty string"
            )

        return value.strip()

    @staticmethod
    def _require_positive_integer(
        container: dict[str, Any],
        field_name: str,
        *,
        parent_name: str,
    ) -> int:
        value = container.get(field_name)

        if (
            not isinstance(value, int)
            or isinstance(value, bool)
            or value < 1
        ):
            raise ValueError(
                f"{parent_name}.{field_name} "
                "must be a positive integer"
            )

        return value

    @staticmethod
    def _require_number(
        container: dict[str, Any],
        field_name: str,
        *,
        parent_name: str,
    ) -> float:
        value = container.get(field_name)

        if (
            not isinstance(value, Real)
            or isinstance(value, bool)
        ):
            raise ValueError(
                f"{parent_name}.{field_name} "
                "must be a real number"
            )

        normalized = float(value)

        if not isfinite(normalized):
            raise ValueError(
                f"{parent_name}.{field_name} "
                "must be finite"
            )

        return normalized
