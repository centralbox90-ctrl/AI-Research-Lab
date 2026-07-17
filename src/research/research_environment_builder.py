from __future__ import annotations

import pandas as pd

from src.application.market_dataset_fingerprint import (
    DatasetFingerprintContext,
    MarketDatasetFingerprinter,
)
from src.research.research_environment import (
    ResearchEnvironmentRef,
)


class MissingDatasetFingerprintError(ValueError):
    """
    Canonical dataset has no fingerprint metadata.
    """


class StaleDatasetFingerprintError(ValueError):
    """
    Dataset fingerprint does not match current dataset.
    """


class UnsupportedFingerprintSchemaError(ValueError):
    """
    Unsupported fingerprint schema version.
    """


class ResearchEnvironmentBuilder:
    """
    Builds immutable ResearchEnvironmentRef only from a
    reproducible canonical market dataset.
    """

    REQUIRED_ATTRS = (
        "content_fingerprint",
        "dataset_fingerprint",
        "fingerprint_algorithm",
        "content_fingerprint_schema_version",
        "dataset_fingerprint_schema_version",
        "normalization_schema_version",
        "symbol",
        "timeframe",
        "closed_bars_policy",
    )

    SUPPORTED_CONTENT_SCHEMA = (
        "market-bars-content-v1"
    )

    SUPPORTED_DATASET_SCHEMA = (
        "market-dataset-fingerprint-v1"
    )

    SUPPORTED_NORMALIZATION_SCHEMA = (
        "market-dataset-v1"
    )

    def __init__(
        self,
        fingerprinter: MarketDatasetFingerprinter | None = None,
    ) -> None:
        self._fingerprinter = (
            fingerprinter
            or MarketDatasetFingerprinter()
        )

    def build(
        self,
        data: pd.DataFrame,
        *,
        assumption_set_fingerprint: str,
        code_version: str,
        executor_version: str,
        statistical_method_version: str,
        random_seed: int,
        verify_dataset: bool = True,
    ) -> ResearchEnvironmentRef:

        self._validate_metadata(data)

        if verify_dataset:
            self._verify_dataset(data)

        return ResearchEnvironmentRef(
            dataset_fingerprint=data.attrs[
                "dataset_fingerprint"
            ],
            assumption_set_fingerprint=(
                assumption_set_fingerprint
            ),
            code_version=code_version,
            executor_version=executor_version,
            statistical_method_version=(
                statistical_method_version
            ),
            random_seed=random_seed,
        )

    def _validate_metadata(
        self,
        data: pd.DataFrame,
    ) -> None:

        missing = [
            key
            for key in self.REQUIRED_ATTRS
            if key not in data.attrs
        ]

        if missing:
            raise MissingDatasetFingerprintError(
                "Canonical dataset has no fingerprint "
                f"metadata. Missing: {missing}"
            )

        if (
            data.attrs[
                "content_fingerprint_schema_version"
            ]
            != self.SUPPORTED_CONTENT_SCHEMA
        ):
            raise UnsupportedFingerprintSchemaError(
                "Unsupported content fingerprint schema."
            )

        if (
            data.attrs[
                "dataset_fingerprint_schema_version"
            ]
            != self.SUPPORTED_DATASET_SCHEMA
        ):
            raise UnsupportedFingerprintSchemaError(
                "Unsupported dataset fingerprint schema."
            )

        if (
            data.attrs[
                "normalization_schema_version"
            ]
            != self.SUPPORTED_NORMALIZATION_SCHEMA
        ):
            raise UnsupportedFingerprintSchemaError(
                "Unsupported normalization schema."
            )

    def _verify_dataset(
        self,
        data: pd.DataFrame,
    ) -> None:

        context = DatasetFingerprintContext(
            symbol=data.attrs["symbol"],
            timeframe=data.attrs["timeframe"],
            closed_bars_policy=data.attrs[
                "closed_bars_policy"
            ],
        )

        if not self._fingerprinter.verify(
            data,
            context,
        ):
            raise StaleDatasetFingerprintError(
                "Dataset fingerprint does not match "
                "current canonical dataset."
            )