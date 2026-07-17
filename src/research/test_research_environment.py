import pytest

from src.research.research_environment import (
    ResearchEnvironmentRef,
)


def create_environment(
    *,
    random_seed: int = 42,
    code_version: str = "git:abc123",
) -> ResearchEnvironmentRef:
    return ResearchEnvironmentRef(
        dataset_fingerprint="dataset:001",
        assumption_set_fingerprint="assumptions:001",
        code_version=code_version,
        executor_version="backtest-engine:v1",
        statistical_method_version="statistics:v1",
        random_seed=random_seed,
    )


def test_environment_fingerprint_is_deterministic() -> None:
    first = create_environment()
    second = create_environment()

    assert first.fingerprint() == second.fingerprint()


def test_environment_fingerprint_changes_with_seed() -> None:
    first = create_environment(random_seed=42)
    second = create_environment(random_seed=43)

    assert first.fingerprint() != second.fingerprint()


def test_environment_fingerprint_changes_with_code_version() -> None:
    first = create_environment(code_version="git:abc123")
    second = create_environment(code_version="git:def456")

    assert first.fingerprint() != second.fingerprint()


def test_environment_rejects_empty_required_text() -> None:
    with pytest.raises(
        ValueError,
        match="dataset_fingerprint",
    ):
        ResearchEnvironmentRef(
            dataset_fingerprint="",
            assumption_set_fingerprint="assumptions:001",
            code_version="git:abc123",
            executor_version="backtest-engine:v1",
            statistical_method_version="statistics:v1",
            random_seed=42,
        )


def test_environment_rejects_boolean_seed() -> None:
    with pytest.raises(
        ValueError,
        match="random_seed must be an integer",
    ):
        create_environment(random_seed=True)
