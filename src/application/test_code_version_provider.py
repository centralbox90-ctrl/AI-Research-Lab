import pytest

from src.application import (
    StaticCodeVersionProvider,
)


def test_static_provider_returns_version() -> None:
    provider = StaticCodeVersionProvider(
        "git:abc123",
    )

    assert (
        provider.get_code_version()
        == "git:abc123"
    )


@pytest.mark.parametrize(
    "value",
    [
        "",
        "   ",
    ],
)
def test_static_provider_rejects_empty_version(
    value: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "code_version must be a non-empty string"
        ),
    ):
        StaticCodeVersionProvider(
            value,
        )