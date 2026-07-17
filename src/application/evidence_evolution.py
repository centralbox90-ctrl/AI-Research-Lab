from dataclasses import dataclass
from typing import Any

from src.application.evidence_metric_delta import (
    EvidenceMetricDelta,
)


@dataclass(frozen=True, init=False)
class EvidenceEvolution:
    previous_evidence: dict[str, Any] | None
    current_evidence: dict[str, Any]
    metric_deltas: tuple[EvidenceMetricDelta, ...]
    change_reason: str | None

    def __init__(
        self,
        previous_evidence: dict[str, Any] | None,
        current_evidence: dict[str, Any],
        change_reason: str | None = None,
        metric_deltas: (
            list[EvidenceMetricDelta]
            | tuple[EvidenceMetricDelta, ...]
            | None
        ) = None,
        *,
        improvement_reason: str | None = None,
    ) -> None:
        if (
            change_reason is not None
            and improvement_reason is not None
            and change_reason != improvement_reason
        ):
            raise ValueError(
                "change_reason and improvement_reason must not contain "
                "different values."
            )

        resolved_change_reason = (
            change_reason
            if change_reason is not None
            else improvement_reason
        )

        resolved_metric_deltas = tuple(
            metric_deltas or ()
        )

        object.__setattr__(
            self,
            "previous_evidence",
            previous_evidence,
        )
        object.__setattr__(
            self,
            "current_evidence",
            current_evidence,
        )
        object.__setattr__(
            self,
            "metric_deltas",
            resolved_metric_deltas,
        )
        object.__setattr__(
            self,
            "change_reason",
            resolved_change_reason,
        )

    @property
    def improvement_reason(self) -> str | None:
        """Backward-compatible alias for the previous field name."""
        return self.change_reason