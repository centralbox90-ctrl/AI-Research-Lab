from __future__ import annotations

from src.application.market_experiment_specification import (
    MarketExperimentSpecification,
)
from src.application.ports.clock import Clock
from src.application.ports.id_generator import (
    IdGenerator,
)
from src.application.system_clock import SystemClock
from src.application.uuid_id_generator import (
    UuidIdGenerator,
)
from src.research.experiment_execution import (
    ExperimentExecution,
)


class ExperimentExecutionFactory:
    """
    Creates one pending execution from a validated specification.

    Identity and time are supplied through Application Layer ports.
    The factory does not prepare data, start execution, persist state,
    or perform runtime scheduling.
    """

    def __init__(
        self,
        *,
        clock: Clock | None = None,
        id_generator: IdGenerator | None = None,
    ) -> None:
        self._clock = clock or SystemClock()
        self._id_generator = (
            id_generator or UuidIdGenerator()
        )

    def create_pending(
        self,
        *,
        specification: MarketExperimentSpecification,
        experiment_id: str,
        correlation_id: str | None = None,
    ) -> ExperimentExecution:
        if not isinstance(
            specification,
            MarketExperimentSpecification,
        ):
            raise TypeError(
                "specification must be a "
                "MarketExperimentSpecification"
            )

        return self.create_pending_from_fingerprint(
            specification_fingerprint=(
                specification.fingerprint
            ),
            experiment_id=experiment_id,
            correlation_id=correlation_id,
        )

    def create_pending_from_fingerprint(
        self,
        *,
        specification_fingerprint: str,
        experiment_id: str,
        correlation_id: str | None = None,
    ) -> ExperimentExecution:
        """
        Create a pending execution from an explicit specification identity.

        This entry point supports execution scenarios whose complete
        specification is not a MarketExperimentSpecification.
        """

        return ExperimentExecution(
            execution_id=(
                self._id_generator.generate()
            ),
            experiment_id=experiment_id,
            specification_fingerprint=(
                specification_fingerprint
            ),
            correlation_id=correlation_id,
            created_at=self._clock.now(),
        )