from src.application.market_experiment_executor import (
    MarketExperimentExecutorFactory,
)


class MarketExperimentExecutorRegistry:
    """
    Registry of supported market experiment executor factories.

    The registry resolves only explicitly registered executor types.
    It does not import arbitrary classes, execute Python code, or
    perform plugin discovery.
    """

    def __init__(self) -> None:
        self._factories: dict[
            str,
            MarketExperimentExecutorFactory,
        ] = {}

    def register(
        self,
        executor_type: str,
        factory: MarketExperimentExecutorFactory,
    ) -> None:
        """
        Register a factory for one executor type.
        """
        if not isinstance(executor_type, str) or not executor_type.strip():
            raise ValueError(
                "executor_type must be a non-empty string"
            )

        normalized_executor_type = executor_type.strip()

        if normalized_executor_type in self._factories:
            raise ValueError(
                f"executor_type already registered: "
                f"{normalized_executor_type}"
            )

        self._factories[normalized_executor_type] = factory

    def get(
        self,
        executor_type: str,
    ) -> MarketExperimentExecutorFactory:
        """
        Return the factory registered for executor_type.
        """
        if not isinstance(executor_type, str) or not executor_type.strip():
            raise ValueError(
                "executor_type must be a non-empty string"
            )

        normalized_executor_type = executor_type.strip()

        try:
            return self._factories[normalized_executor_type]
        except KeyError as error:
            raise LookupError(
                f"unsupported executor_type: "
                f"{normalized_executor_type}"
            ) from error

    def list_executor_types(self) -> list[str]:
        """
        Return registered executor types in deterministic order.
        """
        return sorted(self._factories)