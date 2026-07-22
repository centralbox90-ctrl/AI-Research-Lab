from dataclasses import FrozenInstanceError

import pytest

from src.signals.descriptor import SignalRuleDescriptor


class StubSignalRule:
    def generate(
        self,
        series: object,
        observations: tuple[int, ...],
    ) -> tuple[object, ...]:
        return ()


def test_descriptor_stores_plugin_configuration() -> None:
    rule = StubSignalRule()

    descriptor = SignalRuleDescriptor(
        rule_id="observation-direction",
        version=2,
        rule=rule,
    )

    assert descriptor.rule_id == "observation-direction"
    assert descriptor.version == 2
    assert descriptor.rule is rule


@pytest.mark.parametrize(
    "rule_id",
    [
        "",
        " ",
        "\t",
        "\n",
        "  \t\n  ",
    ],
)
def test_descriptor_rejects_blank_rule_id(
    rule_id: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="rule_id must not be empty",
    ):
        SignalRuleDescriptor(
            rule_id=rule_id,
            version=1,
            rule=StubSignalRule(),
        )


@pytest.mark.parametrize(
    "version",
    [
        0,
        -1,
        -10,
    ],
)
def test_descriptor_rejects_non_positive_version(
    version: int,
) -> None:
    with pytest.raises(
        ValueError,
        match="version must be positive",
    ):
        SignalRuleDescriptor(
            rule_id="valid-rule",
            version=version,
            rule=StubSignalRule(),
        )


@pytest.mark.parametrize(
    "rule",
    [
        object(),
        None,
    ],
)
def test_descriptor_rejects_rule_without_generate(
    rule: object,
) -> None:
    with pytest.raises(
        TypeError,
        match=r"rule must implement generate\(\)",
    ):
        SignalRuleDescriptor(
            rule_id="invalid-rule",
            version=1,
            rule=rule,
        )


def test_descriptor_rejects_non_callable_generate() -> None:
    class InvalidRule:
        generate = "not-callable"

    with pytest.raises(
        TypeError,
        match=r"rule must implement generate\(\)",
    ):
        SignalRuleDescriptor(
            rule_id="invalid-rule",
            version=1,
            rule=InvalidRule(),
        )


def test_descriptor_accepts_callable_generate() -> None:
    class CallableRule:
        generate = staticmethod(lambda series, observations: ())

    rule = CallableRule()

    descriptor = SignalRuleDescriptor(
        rule_id="callable-rule",
        version=1,
        rule=rule,
    )

    assert descriptor.rule is rule


def test_descriptor_is_frozen() -> None:
    descriptor = SignalRuleDescriptor(
        rule_id="immutable-rule",
        version=1,
        rule=StubSignalRule(),
    )

    with pytest.raises(FrozenInstanceError):
        descriptor.version = 2
