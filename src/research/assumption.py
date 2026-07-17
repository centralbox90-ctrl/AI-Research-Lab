from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
import hashlib
import json
from typing import Any


class AssumptionType(StrEnum):
    DATA = "DATA"
    EXECUTION = "EXECUTION"
    COST = "COST"
    INDICATOR = "INDICATOR"
    STATISTICAL = "STATISTICAL"
    MARKET = "MARKET"
    SCOPE = "SCOPE"


class AssumptionStatus(StrEnum):
    ACTIVE = "ACTIVE"
    SUPERSEDED = "SUPERSEDED"
    DEPRECATED = "DEPRECATED"


def _canonicalize(value: Any) -> Any:
    """
    Converts supported values into deterministic JSON-compatible data.
    """

    if isinstance(value, StrEnum):
        return value.value

    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, dict):
        return {
            str(key): _canonicalize(item)
            for key, item in sorted(
                value.items(),
                key=lambda pair: str(pair[0]),
            )
        }

    if isinstance(value, (list, tuple)):
        return [
            _canonicalize(item)
            for item in value
        ]

    if isinstance(value, set):
        canonical_items = [
            _canonicalize(item)
            for item in value
        ]

        return sorted(
            canonical_items,
            key=lambda item: json.dumps(
                item,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            ),
        )

    if value is None or isinstance(
        value,
        (str, int, float, bool),
    ):
        return value

    raise TypeError(
        f"Unsupported assumption value type: "
        f"{type(value).__name__}"
    )


@dataclass(frozen=True)
class Assumption:
    """
    One explicit, versioned research assumption.

    An assumption is immutable. A changed assumption must be represented
    by a new instance with a new version and an optional reference to the
    assumption it supersedes.
    """

    id: str
    type: AssumptionType
    statement: str
    value: Any

    version: int = 1
    scope: tuple[str, ...] = ()
    status: AssumptionStatus = AssumptionStatus.ACTIVE
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    supersedes_assumption_id: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.id, str) or not self.id.strip():
            raise ValueError("id must be a non-empty string")

        if (
            not isinstance(self.statement, str)
            or not self.statement.strip()
        ):
            raise ValueError(
                "statement must be a non-empty string"
            )

        if (
            not isinstance(self.version, int)
            or isinstance(self.version, bool)
            or self.version <= 0
        ):
            raise ValueError(
                "version must be a positive integer"
            )

        if not isinstance(self.created_at, datetime):
            raise ValueError("created_at must be a datetime")

        for scope_item in self.scope:
            if (
                not isinstance(scope_item, str)
                or not scope_item.strip()
            ):
                raise ValueError(
                    "scope must contain only non-empty strings"
                )

        if (
            self.supersedes_assumption_id is not None
            and (
                not isinstance(
                    self.supersedes_assumption_id,
                    str,
                )
                or not self.supersedes_assumption_id.strip()
            )
        ):
            raise ValueError(
                "supersedes_assumption_id must be "
                "a non-empty string or None"
            )

    def fingerprint_payload(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type.value,
            "statement": self.statement,
            "value": _canonicalize(self.value),
            "version": self.version,
            "scope": list(self.scope),
            "status": self.status.value,
            "supersedes_assumption_id": (
                self.supersedes_assumption_id
            ),
        }


@dataclass(frozen=True)
class AssumptionSet:
    """
    Immutable collection of assumptions used by one research campaign.
    """

    id: str
    assumptions: tuple[Assumption, ...]

    version: int = 1
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    supersedes_assumption_set_id: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.id, str) or not self.id.strip():
            raise ValueError("id must be a non-empty string")

        if (
            not isinstance(self.version, int)
            or isinstance(self.version, bool)
            or self.version <= 0
        ):
            raise ValueError(
                "version must be a positive integer"
            )

        if not isinstance(self.assumptions, tuple):
            raise ValueError("assumptions must be a tuple")

        assumption_ids = [
            assumption.id
            for assumption in self.assumptions
        ]

        if len(assumption_ids) != len(set(assumption_ids)):
            raise ValueError(
                "assumption ids must be unique within a set"
            )

        if not isinstance(self.created_at, datetime):
            raise ValueError("created_at must be a datetime")

    def get(self, assumption_id: str) -> Assumption:
        for assumption in self.assumptions:
            if assumption.id == assumption_id:
                return assumption

        raise KeyError(assumption_id)

    def fingerprint(self) -> str:
        """
        Returns a deterministic SHA-256 fingerprint of the set contents.

        The fingerprint excludes creation timestamps and does not depend
        on assumption order or dictionary-key order.
        """

        payload = {
            "version": self.version,
            "supersedes_assumption_set_id": (
                self.supersedes_assumption_set_id
            ),
            "assumptions": [
                assumption.fingerprint_payload()
                for assumption in sorted(
                    self.assumptions,
                    key=lambda item: item.id,
                )
            ],
        }

        serialized = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )

        return hashlib.sha256(
            serialized.encode("utf-8")
        ).hexdigest()
