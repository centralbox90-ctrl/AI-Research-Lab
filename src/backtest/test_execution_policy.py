import pytest

from src.backtest.execution_policy import ExecutionPolicy


def test_execution_policy_accepts_valid_configuration() -> None:
    policy = ExecutionPolicy(
        stop_loss_percent=1.0,
        take_profit_percent=2.0,
        max_holding_bars=24,
        commission_percent=0.1,
        slippage_percent=0.05,
    )

    assert policy.stop_loss_percent == 1.0
    assert policy.take_profit_percent == 2.0
    assert policy.max_holding_bars == 24
    assert policy.commission_percent == 0.1
    assert policy.slippage_percent == 0.05


@pytest.mark.parametrize(
    "field_name,value,message",
    [
        (
            "stop_loss_percent",
            0,
            "stop_loss_percent must be greater than zero",
        ),
        (
            "take_profit_percent",
            0,
            "take_profit_percent must be greater than zero",
        ),
        (
            "max_holding_bars",
            0,
            "max_holding_bars must be a positive integer",
        ),
        (
            "commission_percent",
            -1,
            "commission_percent must not be negative",
        ),
        (
            "slippage_percent",
            -1,
            "slippage_percent must not be negative",
        ),
    ],
)
def test_execution_policy_rejects_invalid_values(
    field_name: str,
    value: object,
    message: str,
) -> None:
    kwargs = {
        "stop_loss_percent": 1.0,
        "take_profit_percent": 2.0,
        "max_holding_bars": 24,
        "commission_percent": 0.0,
        "slippage_percent": 0.0,
    }

    kwargs[field_name] = value

    with pytest.raises(
        ValueError,
        match=message,
    ):
        ExecutionPolicy(**kwargs)