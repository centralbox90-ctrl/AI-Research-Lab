from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any

from src.application.ports.clock import Clock
from src.application.ports.id_generator import (
    IdGenerator,
)
from src.application.system_clock import SystemClock
from src.application.uuid_id_generator import (
    UuidIdGenerator,
)


@dataclass(frozen=True, slots=True)
class ResearchArtifactSourceReference:
    """Exact source reference carried by an artifact envelope."""

    reference_type: str
    reference_id: str
    reference_version: int | None = None
    reference_fingerprint: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "reference_type",
            _normalize_text(
                self.reference_type,
                field_name="reference_type",
            ),
        )
        object.__setattr__(
            self,
            "reference_id",
            _normalize_text(
                self.reference_id,
                field_name="reference_id",
            ),
        )

        if self.reference_version is not None:
            if (
                not isinstance(
                    self.reference_version,
                    int,
                )
                or isinstance(
                    self.reference_version,
                    bool,
                )
            ):
                raise TypeError(
                    "reference_version must be "
                    "an integer or None"
                )

            if self.reference_version <= 0:
                raise ValueError(
                    "reference_version must be positive"
                )

        if self.reference_fingerprint is not None:
            object.__setattr__(
                self,
                "reference_fingerprint",
                _normalize_fingerprint(
                    self.reference_fingerprint,
                    field_name=(
                        "reference_fingerprint"
                    ),
                ),
            )

    def to_dict(self) -> dict[str, object]:
        return {
            "reference_type": self.reference_type,
            "reference_id": self.reference_id,
            "reference_version": (
                self.reference_version
            ),
            "reference_fingerprint": (
                self.reference_fingerprint
            ),
        }


@dataclass(frozen=True, slots=True)
class ResearchArtifactEnvelope:
    """
    Application boundary contract for one serialized artifact.

    Payload and provenance are frozen JSON snapshots. The envelope
    validates integrity but does not interpret payload semantics.
    """

    schema_version: int
    artifact_type: str
    payload_schema_version: int
    artifact_id: str
    created_at: datetime
    producer: str
    producer_version: str
    correlation_id: str | None
    source_references: tuple[
        ResearchArtifactSourceReference,
        ...,
    ]
    provenance: Mapping[str, object]
    payload_fingerprint: str
    payload: Mapping[str, object]

    def __post_init__(self) -> None:
        if (
            not isinstance(self.schema_version, int)
            or isinstance(self.schema_version, bool)
        ):
            raise TypeError(
                "schema_version must be an integer"
            )

        if self.schema_version != 1:
            raise ValueError(
                "schema_version must be 1"
            )

        if (
            not isinstance(
                self.payload_schema_version,
                int,
            )
            or isinstance(
                self.payload_schema_version,
                bool,
            )
        ):
            raise TypeError(
                "payload_schema_version must be "
                "an integer"
            )

        if self.payload_schema_version <= 0:
            raise ValueError(
                "payload_schema_version must be positive"
            )

        for field_name in (
            "artifact_type",
            "artifact_id",
            "producer",
            "producer_version",
        ):
            object.__setattr__(
                self,
                field_name,
                _normalize_text(
                    getattr(self, field_name),
                    field_name=field_name,
                ),
            )

        object.__setattr__(
            self,
            "correlation_id",
            _normalize_optional_text(
                self.correlation_id,
                field_name="correlation_id",
            ),
        )
        object.__setattr__(
            self,
            "created_at",
            _normalize_timestamp(
                self.created_at,
                field_name="created_at",
            ),
        )

        references = tuple(
            self.source_references
        )

        if any(
            not isinstance(
                reference,
                ResearchArtifactSourceReference,
            )
            for reference in references
        ):
            raise TypeError(
                "source_references must contain "
                "ResearchArtifactSourceReference values"
            )

        if len(set(references)) != len(references):
            raise ValueError(
                "source_references must be unique"
            )

        object.__setattr__(
            self,
            "source_references",
            references,
        )

        frozen_provenance = _freeze_json_object(
            self.provenance,
            field_name="provenance",
        )
        frozen_payload = _freeze_json_object(
            self.payload,
            field_name="payload",
        )

        object.__setattr__(
            self,
            "provenance",
            frozen_provenance,
        )
        object.__setattr__(
            self,
            "payload",
            frozen_payload,
        )

        normalized_fingerprint = (
            _normalize_fingerprint(
                self.payload_fingerprint,
                field_name="payload_fingerprint",
            )
        )
        expected_fingerprint = (
            fingerprint_research_artifact_payload(
                frozen_payload
            )
        )

        if (
            normalized_fingerprint
            != expected_fingerprint
        ):
            raise ValueError(
                "payload_fingerprint does not match payload"
            )

        object.__setattr__(
            self,
            "payload_fingerprint",
            normalized_fingerprint,
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "artifact_type": self.artifact_type,
            "payload_schema_version": (
                self.payload_schema_version
            ),
            "artifact_id": self.artifact_id,
            "created_at": self.created_at.isoformat(),
            "producer": self.producer,
            "producer_version": self.producer_version,
            "correlation_id": self.correlation_id,
            "source_references": [
                reference.to_dict()
                for reference in self.source_references
            ],
            "provenance": _thaw_json(
                self.provenance
            ),
            "payload_fingerprint": (
                self.payload_fingerprint
            ),
            "payload": _thaw_json(
                self.payload
            ),
        }


class ResearchArtifactEnvelopeFactory:
    """Creates validated version-one artifact envelopes."""

    def __init__(
        self,
        *,
        producer: str,
        producer_version: str,
        clock: Clock | None = None,
        id_generator: IdGenerator | None = None,
    ) -> None:
        self._producer = _normalize_text(
            producer,
            field_name="producer",
        )
        self._producer_version = _normalize_text(
            producer_version,
            field_name="producer_version",
        )
        self._clock = clock or SystemClock()
        self._id_generator = (
            id_generator or UuidIdGenerator()
        )

    def create(
        self,
        *,
        artifact_type: str,
        payload_schema_version: int,
        payload: Mapping[str, object],
        provenance: Mapping[str, object],
        correlation_id: str | None = None,
        source_references: tuple[
            ResearchArtifactSourceReference,
            ...,
        ] = (),
    ) -> ResearchArtifactEnvelope:
        return ResearchArtifactEnvelope(
            schema_version=1,
            artifact_type=artifact_type,
            payload_schema_version=(
                payload_schema_version
            ),
            artifact_id=(
                self._id_generator.generate()
            ),
            created_at=self._clock.now(),
            producer=self._producer,
            producer_version=self._producer_version,
            correlation_id=correlation_id,
            source_references=source_references,
            provenance=provenance,
            payload_fingerprint=(
                fingerprint_research_artifact_payload(
                    payload
                )
            ),
            payload=payload,
        )


def fingerprint_research_artifact_payload(
    payload: Mapping[str, object],
) -> str:
    frozen_payload = _freeze_json_object(
        payload,
        field_name="payload",
    )
    serialized = json.dumps(
        _thaw_json(frozen_payload),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )

    return hashlib.sha256(
        serialized.encode("utf-8")
    ).hexdigest()


def _freeze_json_object(
    value: object,
    *,
    field_name: str,
) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise TypeError(
            f"{field_name} must be a mapping"
        )

    frozen = _freeze_json(
        value,
        path=field_name,
    )

    if not isinstance(frozen, Mapping):
        raise TypeError(
            f"{field_name} must be a mapping"
        )

    return frozen


def _freeze_json(
    value: object,
    *,
    path: str,
) -> object:
    if value is None or isinstance(
        value,
        (str, bool, int),
    ):
        return value

    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError(
                f"{path} contains a non-finite number"
            )

        return value

    if isinstance(value, Mapping):
        items = list(value.items())

        if any(
            not isinstance(key, str)
            for key, _ in items
        ):
            raise TypeError(
                f"{path} contains a non-string key"
            )

        return MappingProxyType(
            {
                key: _freeze_json(
                    item,
                    path=f"{path}.{key}",
                )
                for key, item in sorted(
                    items,
                    key=lambda pair: pair[0],
                )
            }
        )

    if isinstance(value, (list, tuple)):
        return tuple(
            _freeze_json(
                item,
                path=f"{path}[{index}]",
            )
            for index, item in enumerate(value)
        )

    raise TypeError(
        f"{path} contains a non-JSON value: "
        f"{type(value).__name__}"
    )


def _thaw_json(
    value: object,
) -> Any:
    if isinstance(value, Mapping):
        return {
            key: _thaw_json(item)
            for key, item in value.items()
        }

    if isinstance(value, tuple):
        return [
            _thaw_json(item)
            for item in value
        ]

    return value


def _normalize_text(
    value: object,
    *,
    field_name: str,
) -> str:
    if not isinstance(value, str):
        raise TypeError(
            f"{field_name} must be a string"
        )

    normalized = value.strip()

    if not normalized:
        raise ValueError(
            f"{field_name} must not be empty"
        )

    return normalized


def _normalize_optional_text(
    value: object,
    *,
    field_name: str,
) -> str | None:
    if value is None:
        return None

    return _normalize_text(
        value,
        field_name=field_name,
    )


def _normalize_fingerprint(
    value: object,
    *,
    field_name: str,
) -> str:
    normalized = _normalize_text(
        value,
        field_name=field_name,
    )

    if (
        len(normalized) != 64
        or any(
            character not in "0123456789abcdef"
            for character in normalized
        )
    ):
        raise ValueError(
            f"{field_name} must be a lowercase "
            "SHA-256 hexadecimal string"
        )

    return normalized


def _normalize_timestamp(
    value: object,
    *,
    field_name: str,
) -> datetime:
    if not isinstance(value, datetime):
        raise TypeError(
            f"{field_name} must be a datetime"
        )

    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(
            f"{field_name} must be timezone-aware"
        )

    return value.astimezone(timezone.utc)
