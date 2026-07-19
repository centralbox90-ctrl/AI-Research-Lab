from __future__ import annotations

from dataclasses import dataclass
import hashlib
import struct

import numpy as np
import pandas as pd


class MarketDatasetContractError(ValueError):
    """
    Base error for canonical market dataset contract violations.
    """


class MissingMarketDatasetColumnError(
    MarketDatasetContractError,
):
    """
    Raised when a required market dataset column is absent.
    """


class InvalidMarketDatasetValueError(
    MarketDatasetContractError,
):
    """
    Raised when market data cannot be represented canonically.
    """


class DuplicateMarketDatasetTimestampError(
    MarketDatasetContractError,
):
    """
    Raised when the dataset contains duplicate timestamps.
    """


@dataclass(frozen=True)
class DatasetFingerprintContext:
    """
    Stable research identity surrounding canonical market bars.
    """

    symbol: str
    timeframe: str
    closed_bars_policy: str = "closed-bars-only-v1"

    def __post_init__(self) -> None:
        required_fields = {
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "closed_bars_policy": self.closed_bars_policy,
        }

        for field_name, value in required_fields.items():
            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    f"{field_name} must be a non-empty string"
                )


@dataclass(frozen=True)
class MarketDatasetFingerprint:
    """
    Versioned fingerprints for canonical market data.
    """

    content_fingerprint: str
    dataset_fingerprint: str
    algorithm: str
    content_schema_version: str
    dataset_schema_version: str
    normalization_schema_version: str


class MarketDatasetCanonicalizer:
    """
    Creates Canonical Market Dataset v1.

    Canonical columns:

    timestamp
    open
    high
    low
    close
    tick_volume
    """

    NORMALIZATION_SCHEMA_VERSION = "market-dataset-v1"

    REQUIRED_COLUMNS = (
        "timestamp",
        "open",
        "high",
        "low",
        "close",
        "tick_volume",
    )

    PRICE_COLUMNS = (
        "open",
        "high",
        "low",
        "close",
    )

    def canonicalize(
        self,
        data: pd.DataFrame,
    ) -> pd.DataFrame:
        if not isinstance(data, pd.DataFrame):
            raise TypeError(
                "market dataset must be a pandas DataFrame"
            )

        missing_columns = [
            column
            for column in self.REQUIRED_COLUMNS
            if column not in data.columns
        ]

        if missing_columns:
            raise MissingMarketDatasetColumnError(
                "market dataset is missing required columns: "
                + ", ".join(missing_columns)
            )

        canonical = data.loc[
            :,
            list(self.REQUIRED_COLUMNS),
        ].copy()

        # Metadata from the source DataFrame cannot be trusted after
        # a content-changing canonicalization operation.
        canonical.attrs = {}

        canonical["timestamp"] = self._canonicalize_timestamp(
            canonical["timestamp"]
        )

        for column in self.PRICE_COLUMNS:
            canonical[column] = self._canonicalize_price(
                canonical[column],
                column,
            )

        canonical["tick_volume"] = self._canonicalize_volume(
            canonical["tick_volume"]
        )

        canonical = canonical.sort_values(
            "timestamp",
            kind="mergesort",
        ).reset_index(drop=True)

        duplicate_mask = canonical["timestamp"].duplicated(
            keep=False
        )

        if duplicate_mask.any():
            duplicate_examples = (
                canonical.loc[
                    duplicate_mask,
                    "timestamp",
                ]
                .head(5)
                .tolist()
            )

            raise DuplicateMarketDatasetTimestampError(
                "market dataset contains duplicate timestamps: "
                f"{duplicate_examples}"
            )

        if not canonical["timestamp"].is_monotonic_increasing:
            raise InvalidMarketDatasetValueError(
                "market dataset timestamps must be increasing"
            )

        canonical.attrs[
            "normalization_schema_version"
        ] = self.NORMALIZATION_SCHEMA_VERSION

        return canonical

    def _canonicalize_timestamp(
        self,
        values: pd.Series,
    ) -> pd.Series:
        try:
            timestamps = pd.to_datetime(
                values,
                utc=True,
                errors="raise",
            )
        except (
            TypeError,
            ValueError,
            OverflowError,
        ) as error:
            raise InvalidMarketDatasetValueError(
                "timestamp values must be convertible to UTC"
            ) from error

        if timestamps.isna().any():
            raise InvalidMarketDatasetValueError(
                "timestamp cannot contain missing values"
            )

        nanoseconds = timestamps.astype("int64")

        return pd.Series(
            nanoseconds.to_numpy(
                dtype="<i8",
                copy=True,
            ),
            index=values.index,
            dtype="int64",
        )

    def _canonicalize_price(
        self,
        values: pd.Series,
        column: str,
    ) -> pd.Series:
        try:
            numeric = pd.to_numeric(
                values,
                errors="raise",
            )

            canonical_values = numeric.to_numpy(
                dtype="<f8",
                copy=True,
            )
        except (
            TypeError,
            ValueError,
            OverflowError,
        ) as error:
            raise InvalidMarketDatasetValueError(
                f"{column} must be convertible to float64"
            ) from error

        if not np.isfinite(canonical_values).all():
            raise InvalidMarketDatasetValueError(
                f"{column} cannot contain NaN or infinity"
            )

        return pd.Series(
            canonical_values,
            index=values.index,
            dtype="float64",
        )

    def _canonicalize_volume(
        self,
        values: pd.Series,
    ) -> pd.Series:
        try:
            numeric = pd.to_numeric(
                values,
                errors="raise",
            )
        except (
            TypeError,
            ValueError,
        ) as error:
            raise InvalidMarketDatasetValueError(
                "tick_volume must be convertible to int64"
            ) from error

        if numeric.isna().any():
            raise InvalidMarketDatasetValueError(
                "tick_volume cannot contain missing values"
            )

        float_values = numeric.to_numpy(
            dtype="<f8",
            copy=False,
        )

        if not np.isfinite(float_values).all():
            raise InvalidMarketDatasetValueError(
                "tick_volume cannot contain infinity"
            )

        if not np.equal(
            float_values,
            np.trunc(float_values),
        ).all():
            raise InvalidMarketDatasetValueError(
                "tick_volume must contain integer values"
            )

        if (float_values < 0).any():
            raise InvalidMarketDatasetValueError(
                "tick_volume cannot contain negative values"
            )

        try:
            canonical_values = numeric.to_numpy(
                dtype="<i8",
                copy=True,
            )
        except (
            TypeError,
            ValueError,
            OverflowError,
        ) as error:
            raise InvalidMarketDatasetValueError(
                "tick_volume is outside the int64 range"
            ) from error

        return pd.Series(
            canonical_values,
            index=values.index,
            dtype="int64",
        )


class MarketDatasetFingerprinter:
    """
    Calculates versioned content and dataset fingerprints.
    """

    ALGORITHM = "sha256"

    CONTENT_SCHEMA_VERSION = "market-bars-content-v1"
    DATASET_SCHEMA_VERSION = "market-dataset-fingerprint-v1"

    CONTENT_DOMAIN = (
        b"ai-research-lab:market-bars-content:v1"
    )

    DATASET_DOMAIN = (
        b"ai-research-lab:market-dataset:v1"
    )

    def calculate(
        self,
        canonical_data: pd.DataFrame,
        context: DatasetFingerprintContext,
    ) -> MarketDatasetFingerprint:
        content_fingerprint = (
            self.calculate_content_fingerprint(
                canonical_data
            )
        )

        dataset_fingerprint = (
            self.calculate_dataset_fingerprint(
                content_fingerprint,
                context,
            )
        )

        return MarketDatasetFingerprint(
            content_fingerprint=content_fingerprint,
            dataset_fingerprint=dataset_fingerprint,
            algorithm=self.ALGORITHM,
            content_schema_version=(
                self.CONTENT_SCHEMA_VERSION
            ),
            dataset_schema_version=(
                self.DATASET_SCHEMA_VERSION
            ),
            normalization_schema_version=(
                MarketDatasetCanonicalizer
                .NORMALIZATION_SCHEMA_VERSION
            ),
        )

    def attach(
        self,
        canonical_data: pd.DataFrame,
        context: DatasetFingerprintContext,
    ) -> MarketDatasetFingerprint:
        fingerprint = self.calculate(
            canonical_data,
            context,
        )

        canonical_data.attrs.update(
            {
                "content_fingerprint": (
                    fingerprint.content_fingerprint
                ),
                "dataset_fingerprint": (
                    fingerprint.dataset_fingerprint
                ),
                "fingerprint_algorithm": (
                    fingerprint.algorithm
                ),
                "content_fingerprint_schema_version": (
                    fingerprint.content_schema_version
                ),
                "dataset_fingerprint_schema_version": (
                    fingerprint.dataset_schema_version
                ),
                "normalization_schema_version": (
                    fingerprint.normalization_schema_version
                ),
                "symbol": context.symbol.strip().upper(),
                "timeframe": (
                    context.timeframe.strip().upper()
                ),
                "closed_bars_policy": (
                    context.closed_bars_policy.strip()
                ),
            }
        )

        return fingerprint

    def verify(
        self,
        canonical_data: pd.DataFrame,
        context: DatasetFingerprintContext,
    ) -> bool:
        calculated = self.calculate(
            canonical_data,
            context,
        )

        return (
            canonical_data.attrs.get(
                "content_fingerprint"
            )
            == calculated.content_fingerprint
            and canonical_data.attrs.get(
                "dataset_fingerprint"
            )
            == calculated.dataset_fingerprint
        )

    def calculate_content_fingerprint(
        self,
        canonical_data: pd.DataFrame,
    ) -> str:
        expected_columns = (
            MarketDatasetCanonicalizer.REQUIRED_COLUMNS
        )

        if tuple(canonical_data.columns) != expected_columns:
            raise MarketDatasetContractError(
                "market dataset is not canonical: "
                f"expected columns {expected_columns}, "
                f"received {tuple(canonical_data.columns)}"
            )

        digest = hashlib.sha256()

        self._write_bytes(
            digest,
            self.CONTENT_DOMAIN,
        )

        self._write_unsigned_integer(
            digest,
            len(canonical_data),
        )

        column_types = {
            "timestamp": ("int64", "<i8"),
            "open": ("float64", "<f8"),
            "high": ("float64", "<f8"),
            "low": ("float64", "<f8"),
            "close": ("float64", "<f8"),
            "tick_volume": ("int64", "<i8"),
        }

        for column in expected_columns:
            type_name, numpy_type = column_types[column]

            payload = canonical_data[column].to_numpy(
                dtype=numpy_type,
                copy=True,
            ).tobytes(order="C")

            self._write_text(
                digest,
                column,
            )
            self._write_text(
                digest,
                type_name,
            )
            self._write_unsigned_integer(
                digest,
                len(canonical_data),
            )
            self._write_bytes(
                digest,
                payload,
            )

        return (
            "sha256:market-bars-content:v1:"
            + digest.hexdigest()
        )

    def calculate_dataset_fingerprint(
        self,
        content_fingerprint: str,
        context: DatasetFingerprintContext,
    ) -> str:
        digest = hashlib.sha256()

        self._write_bytes(
            digest,
            self.DATASET_DOMAIN,
        )

        fields = (
            (
                "content_fingerprint",
                content_fingerprint,
            ),
            (
                "symbol",
                context.symbol.strip().upper(),
            ),
            (
                "timeframe",
                context.timeframe.strip().upper(),
            ),
            (
                "normalization_schema_version",
                MarketDatasetCanonicalizer
                .NORMALIZATION_SCHEMA_VERSION,
            ),
            (
                "closed_bars_policy",
                context.closed_bars_policy.strip(),
            ),
        )

        for field_name, value in fields:
            self._write_text(
                digest,
                field_name,
            )
            self._write_text(
                digest,
                value,
            )

        return (
            "sha256:market-dataset:v1:"
            + digest.hexdigest()
        )

    def _write_text(
        self,
        digest: object,
        value: str,
    ) -> None:
        self._write_bytes(
            digest,
            value.encode("utf-8"),
        )

    def _write_bytes(
        self,
        digest: object,
        value: bytes,
    ) -> None:
        self._write_unsigned_integer(
            digest,
            len(value),
        )
        digest.update(value)

    def _write_unsigned_integer(
        self,
        digest: object,
        value: int,
    ) -> None:
        digest.update(
            struct.pack(
                "<Q",
                value,
            )
        )