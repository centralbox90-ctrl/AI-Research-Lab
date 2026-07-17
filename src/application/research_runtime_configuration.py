from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ResearchRuntimeConfiguration:
    """
    Immutable runtime configuration used to build reproducible
    research environments.

    The composition root supplies these values. Research services must
    not hardcode runtime versions or random seeds.
    """

    code_version: str
    executor_version: str
    statistical_method_version: str
    random_seed: int

    def __post_init__(self) -> None:
        required_text_fields = {
            "code_version": self.code_version,
            "executor_version": self.executor_version,
            "statistical_method_version": (
                self.statistical_method_version
            ),
        }

        for field_name, value in required_text_fields.items():
            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    f"{field_name} must be a non-empty string"
                )

        if (
            not isinstance(self.random_seed, int)
            or isinstance(self.random_seed, bool)
        ):
            raise ValueError(
                "random_seed must be an integer"
            )