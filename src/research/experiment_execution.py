from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from enum import StrEnum
from typing import Self


class ExperimentExecutionStatus(StrEnum):
    """Technical state of one experiment execution attempt."""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class ExperimentExecutionFailureStage(StrEnum):
    """Technical stage that prevented execution completion."""

    PREPARATION = "PREPARATION"
    EXECUTION = "EXECUTION"


@dataclass(frozen=True, slots=True)
class ExperimentExecutionFailure:
    """Sanitized technical failure attached to a failed execution."""

    stage: ExperimentExecutionFailureStage
    error_type: str
    message: str

    def __post_init__(self) -> None:
        if not isinstance(
            self.stage,
            ExperimentExecutionFailureStage,
        ):
            raise TypeError(
                "stage must be an "
                "ExperimentExecutionFailureStage"
            )

        object.__setattr__(
            self,
            "error_type",
            _normalize_text(
                self.error_type,
                field_name="error_type",
            ),
        )
        object.__setattr__(
            self,
            "message",
            _normalize_text(
                self.message,
                field_name="message",
            ),
        )

    def to_dict(self) -> dict[str, str]:
        return {
            "stage": self.stage.value,
            "error_type": self.error_type,
            "message": self.message,
        }


@dataclass(frozen=True, slots=True)
class ExperimentExecution:
    """
    Immutable state of one attempt to execute one experiment.

    Identity and timestamps are supplied by the Application Layer.
    Transition methods return new instances and never mutate a
    terminal execution.
    """

    execution_id: str
    experiment_id: str
    specification_fingerprint: str
    created_at: datetime
    correlation_id: str | None = None
    environment_fingerprint: str | None = None
    status: ExperimentExecutionStatus = (
        ExperimentExecutionStatus.PENDING
    )
    started_at: datetime | None = None
    finished_at: datetime | None = None
    result_id: str | None = None
    failure: ExperimentExecutionFailure | None = None

    def __post_init__(self) -> None:
        if not isinstance(
            self.status,
            ExperimentExecutionStatus,
        ):
            raise TypeError(
                "status must be an "
                "ExperimentExecutionStatus"
            )

        if (
            self.failure is not None
            and not isinstance(
                self.failure,
                ExperimentExecutionFailure,
            )
        ):
            raise TypeError(
                "failure must be an "
                "ExperimentExecutionFailure or None"
            )

        object.__setattr__(
            self,
            "execution_id",
            _normalize_text(
                self.execution_id,
                field_name="execution_id",
            ),
        )
        object.__setattr__(
            self,
            "experiment_id",
            _normalize_text(
                self.experiment_id,
                field_name="experiment_id",
            ),
        )
        object.__setattr__(
            self,
            "specification_fingerprint",
            _normalize_fingerprint(
                self.specification_fingerprint,
                field_name="specification_fingerprint",
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
            "environment_fingerprint",
            _normalize_optional_fingerprint(
                self.environment_fingerprint,
                field_name="environment_fingerprint",
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
        object.__setattr__(
            self,
            "started_at",
            _normalize_optional_timestamp(
                self.started_at,
                field_name="started_at",
            ),
        )
        object.__setattr__(
            self,
            "finished_at",
            _normalize_optional_timestamp(
                self.finished_at,
                field_name="finished_at",
            ),
        )
        object.__setattr__(
            self,
            "result_id",
            _normalize_optional_text(
                self.result_id,
                field_name="result_id",
            ),
        )

        self._validate_timeline()
        self._validate_state()

    @property
    def is_terminal(self) -> bool:
        return self.status in {
            ExperimentExecutionStatus.SUCCEEDED,
            ExperimentExecutionStatus.FAILED,
            ExperimentExecutionStatus.CANCELLED,
        }

    def start(
        self,
        *,
        environment_fingerprint: str,
        started_at: datetime,
    ) -> Self:
        self._require_status(
            ExperimentExecutionStatus.PENDING
        )

        return replace(
            self,
            environment_fingerprint=(
                environment_fingerprint
            ),
            status=ExperimentExecutionStatus.RUNNING,
            started_at=started_at,
        )

    def succeed(
        self,
        *,
        result_id: str,
        finished_at: datetime,
    ) -> Self:
        self._require_status(
            ExperimentExecutionStatus.RUNNING
        )

        return replace(
            self,
            status=ExperimentExecutionStatus.SUCCEEDED,
            finished_at=finished_at,
            result_id=result_id,
        )

    def fail(
        self,
        *,
        failure: ExperimentExecutionFailure,
        finished_at: datetime,
    ) -> Self:
        self._require_status(
            ExperimentExecutionStatus.PENDING,
            ExperimentExecutionStatus.RUNNING,
        )

        if not isinstance(
            failure,
            ExperimentExecutionFailure,
        ):
            raise TypeError(
                "failure must be an "
                "ExperimentExecutionFailure"
            )

        expected_stage = (
            ExperimentExecutionFailureStage.PREPARATION
            if self.status
            is ExperimentExecutionStatus.PENDING
            else ExperimentExecutionFailureStage.EXECUTION
        )

        if failure.stage is not expected_stage:
            raise ValueError(
                "failure stage does not match "
                "the current execution status"
            )

        return replace(
            self,
            status=ExperimentExecutionStatus.FAILED,
            finished_at=finished_at,
            failure=failure,
        )

    def cancel(
        self,
        *,
        finished_at: datetime,
    ) -> Self:
        self._require_status(
            ExperimentExecutionStatus.PENDING,
            ExperimentExecutionStatus.RUNNING,
        )

        return replace(
            self,
            status=ExperimentExecutionStatus.CANCELLED,
            finished_at=finished_at,
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": 1,
            "execution_id": self.execution_id,
            "experiment_id": self.experiment_id,
            "specification_fingerprint": (
                self.specification_fingerprint
            ),
            "correlation_id": self.correlation_id,
            "environment_fingerprint": (
                self.environment_fingerprint
            ),
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "started_at": (
                self.started_at.isoformat()
                if self.started_at is not None
                else None
            ),
            "finished_at": (
                self.finished_at.isoformat()
                if self.finished_at is not None
                else None
            ),
            "result_id": self.result_id,
            "failure": (
                self.failure.to_dict()
                if self.failure is not None
                else None
            ),
        }

    def _require_status(
        self,
        *allowed: ExperimentExecutionStatus,
    ) -> None:
        if self.status not in allowed:
            allowed_values = ", ".join(
                status.value
                for status in allowed
            )
            raise ValueError(
                "execution status must be one of: "
                f"{allowed_values}"
            )

    def _validate_timeline(self) -> None:
        if (
            self.started_at is not None
            and self.started_at < self.created_at
        ):
            raise ValueError(
                "started_at must not be earlier "
                "than created_at"
            )

        if (
            self.finished_at is not None
            and self.finished_at < self.created_at
        ):
            raise ValueError(
                "finished_at must not be earlier "
                "than created_at"
            )

        if (
            self.started_at is not None
            and self.finished_at is not None
            and self.finished_at < self.started_at
        ):
            raise ValueError(
                "finished_at must not be earlier "
                "than started_at"
            )

    def _validate_state(self) -> None:
        if self.status is ExperimentExecutionStatus.PENDING:
            if any(
                value is not None
                for value in (
                    self.environment_fingerprint,
                    self.started_at,
                    self.finished_at,
                    self.result_id,
                    self.failure,
                )
            ):
                raise ValueError(
                    "PENDING execution cannot contain "
                    "runtime outcome fields"
                )
            return

        if self.status is ExperimentExecutionStatus.RUNNING:
            if (
                self.environment_fingerprint is None
                or self.started_at is None
            ):
                raise ValueError(
                    "RUNNING execution requires environment "
                    "fingerprint and started_at"
                )

            if any(
                value is not None
                for value in (
                    self.finished_at,
                    self.result_id,
                    self.failure,
                )
            ):
                raise ValueError(
                    "RUNNING execution cannot contain "
                    "terminal outcome fields"
                )
            return

        if self.status is ExperimentExecutionStatus.SUCCEEDED:
            if (
                self.environment_fingerprint is None
                or self.started_at is None
                or self.finished_at is None
                or self.result_id is None
            ):
                raise ValueError(
                    "SUCCEEDED execution requires environment, "
                    "timestamps, and result_id"
                )

            if self.failure is not None:
                raise ValueError(
                    "SUCCEEDED execution cannot contain failure"
                )
            return

        if self.status is ExperimentExecutionStatus.FAILED:
            if self.finished_at is None or self.failure is None:
                raise ValueError(
                    "FAILED execution requires finished_at "
                    "and failure"
                )

            if self.result_id is not None:
                raise ValueError(
                    "FAILED execution cannot contain result_id"
                )

            if self.started_at is None:
                if (
                    self.failure.stage
                    is not
                    ExperimentExecutionFailureStage.PREPARATION
                ):
                    raise ValueError(
                        "failure before start must use "
                        "PREPARATION stage"
                    )
            else:
                if self.environment_fingerprint is None:
                    raise ValueError(
                        "started FAILED execution requires "
                        "environment fingerprint"
                    )

                if (
                    self.failure.stage
                    is not
                    ExperimentExecutionFailureStage.EXECUTION
                ):
                    raise ValueError(
                        "failure after start must use "
                        "EXECUTION stage"
                    )
            return

        if self.status is ExperimentExecutionStatus.CANCELLED:
            if self.finished_at is None:
                raise ValueError(
                    "CANCELLED execution requires finished_at"
                )

            if self.result_id is not None or self.failure is not None:
                raise ValueError(
                    "CANCELLED execution cannot contain "
                    "result or failure"
                )

            if self.started_at is None:
                if self.environment_fingerprint is not None:
                    raise ValueError(
                        "execution cancelled before start "
                        "cannot contain environment fingerprint"
                    )
            elif self.environment_fingerprint is None:
                raise ValueError(
                    "started CANCELLED execution requires "
                    "environment fingerprint"
                )


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


def _normalize_optional_fingerprint(
    value: object,
    *,
    field_name: str,
) -> str | None:
    if value is None:
        return None

    return _normalize_fingerprint(
        value,
        field_name=field_name,
    )


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


def _normalize_optional_timestamp(
    value: object,
    *,
    field_name: str,
) -> datetime | None:
    if value is None:
        return None

    return _normalize_timestamp(
        value,
        field_name=field_name,
    )