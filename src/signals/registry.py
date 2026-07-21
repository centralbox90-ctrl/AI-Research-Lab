from __future__ import annotations

from types import MappingProxyType

from src.signals.descriptor import (
    SignalRuleDescriptor,
)


class SignalRuleRegistry:
    """
    Resolves signal rules by id.
    """

    def __init__(
        self,
        descriptors: tuple[
            SignalRuleDescriptor,
            ...,
        ],
    ) -> None:

        registry = {}

        for descriptor in descriptors:

            if descriptor.rule_id in registry:
                raise ValueError(
                    "Duplicate signal rule: "
                    f"{descriptor.rule_id}"
                )

            registry[
                descriptor.rule_id
            ] = descriptor

        self._registry = MappingProxyType(
            registry
        )

    def get(
        self,
        rule_id: str,
    ):
        descriptor = self._registry.get(
            rule_id,
        )

        if descriptor is None:
            raise KeyError(
                f"Unknown signal rule: {rule_id}"
            )

        return descriptor.rule