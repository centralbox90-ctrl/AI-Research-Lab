from typing import Any

from src.application.evidence_metric_delta import (
    EvidenceMetricDelta,
)


class EvidenceMetricDeltaBuilder:
    def build(
        self,
        previous_evidence: dict[str, Any] | None,
        current_evidence: dict[str, Any],
    ) -> list[EvidenceMetricDelta]:
        previous = previous_evidence or {}

        metric_names = sorted(
            set(previous) | set(current_evidence)
        )

        return [
            self._build_metric_delta(
                metric_name=metric_name,
                previous=previous,
                current=current_evidence,
            )
            for metric_name in metric_names
        ]

    def _build_metric_delta(
        self,
        metric_name: str,
        previous: dict[str, Any],
        current: dict[str, Any],
    ) -> EvidenceMetricDelta:
        previous_exists = metric_name in previous
        current_exists = metric_name in current

        previous_value = previous.get(metric_name)
        current_value = current.get(metric_name)

        if not previous_exists:
            return EvidenceMetricDelta(
                metric_name=metric_name,
                previous_value=None,
                current_value=current_value,
                absolute_delta=None,
                direction="added",
            )

        if not current_exists:
            return EvidenceMetricDelta(
                metric_name=metric_name,
                previous_value=previous_value,
                current_value=None,
                absolute_delta=None,
                direction="removed",
            )

        if previous_value == current_value:
            return EvidenceMetricDelta(
                metric_name=metric_name,
                previous_value=previous_value,
                current_value=current_value,
                absolute_delta=0.0,
                direction="unchanged",
            )

        if self._is_numeric(previous_value) and self._is_numeric(
            current_value
        ):
            absolute_delta = float(
                current_value - previous_value
            )

            direction = (
                "increased"
                if absolute_delta > 0
                else "decreased"
            )

            return EvidenceMetricDelta(
                metric_name=metric_name,
                previous_value=previous_value,
                current_value=current_value,
                absolute_delta=absolute_delta,
                direction=direction,
            )

        return EvidenceMetricDelta(
            metric_name=metric_name,
            previous_value=previous_value,
            current_value=current_value,
            absolute_delta=None,
            direction="not_comparable",
        )

    def _is_numeric(
        self,
        value: Any,
    ) -> bool:
        return (
            isinstance(value, (int, float))
            and not isinstance(value, bool)
        )