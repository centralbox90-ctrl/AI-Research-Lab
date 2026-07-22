import pytest

from src.signals.descriptor import SignalRuleDescriptor
from src.signals.registry import SignalRuleRegistry


class StubSignalRule:
    def generate(
        self,
        series: object,
        observations: tuple[int, ...],
    ) -> tuple[object, ...]:
        return ()


def build_descriptor(
    *,
    rule_id: str = "observation-direction",
    rule: object | None = None,
) -> SignalRuleDescriptor:
    return SignalRuleDescriptor(
        rule_id=rule_id,
        version=1,
        rule=rule or StubSignalRule(),
    )


def test_get_returns_registered_rule() -> None:
    rule = StubSignalRule()
    registry = SignalRuleRegistry(
        (
            build_descriptor(
                rule=rule,
            ),
        )
    )

    result = registry.get(
        "observation-direction",
    )

    assert result is rule


def test_get_resolves_correct_rule() -> None:
    first_rule = StubSignalRule()
    second_rule = StubSignalRule()

    registry = SignalRuleRegistry(
        (
            build_descriptor(
                rule_id="first",
                rule=first_rule,
            ),
            build_descriptor(
                rule_id="second",
                rule=second_rule,
            ),
        )
    )

    assert registry.get("first") is first_rule
    assert registry.get("second") is second_rule


def test_duplicate_rule_id_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="Duplicate signal rule: duplicate",
    ):
        SignalRuleRegistry(
            (
                build_descriptor(
                    rule_id="duplicate",
                ),
                build_descriptor(
                    rule_id="duplicate",
                ),
            )
        )


def test_unknown_rule_id_is_rejected() -> None:
    registry = SignalRuleRegistry(())

    with pytest.raises(
        KeyError,
        match="Unknown signal rule: missing",
    ):
        registry.get("missing")


def test_rule_id_is_not_normalized_by_registry() -> None:
    rule = StubSignalRule()
    registry = SignalRuleRegistry(
        (
            build_descriptor(
                rule_id="exact-id",
                rule=rule,
            ),
        )
    )

    with pytest.raises(
        KeyError,
        match="Unknown signal rule",
    ):
        registry.get(" exact-id ")
