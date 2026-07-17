from dataclasses import dataclass
import hashlib
import json


@dataclass(frozen=True)
class ResearchEnvironmentRef:
    """
    Minimal immutable reference to a reproducible research environment.
    """

    dataset_fingerprint: str
    assumption_set_fingerprint: str
    code_version: str
    executor_version: str
    statistical_method_version: str
    random_seed: int

    def __post_init__(self) -> None:
        required_text_fields = {
            "dataset_fingerprint": self.dataset_fingerprint,
            "assumption_set_fingerprint": (
                self.assumption_set_fingerprint
            ),
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
            raise ValueError("random_seed must be an integer")

    def fingerprint(self) -> str:
        payload = {
            "dataset_fingerprint": self.dataset_fingerprint,
            "assumption_set_fingerprint": (
                self.assumption_set_fingerprint
            ),
            "code_version": self.code_version,
            "executor_version": self.executor_version,
            "statistical_method_version": (
                self.statistical_method_version
            ),
            "random_seed": self.random_seed,
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
