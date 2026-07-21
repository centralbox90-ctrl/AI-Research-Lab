from unittest.mock import Mock

import pandas as pd

from src.indicators.calculation_service import (
    IndicatorCalculationService,
)


def test_calculate_uses_descriptor_calculator() -> None:
    data = pd.DataFrame(
        {
            "close": [100.0, 101.0],
        }
    )

    specification = Mock()
    specification.indicator_type = "test_indicator"

    expected_series = Mock()

    calculator = Mock(
        return_value=expected_series,
    )

    descriptor = Mock()
    descriptor.calculator = calculator

    catalog = Mock()
    catalog.get.return_value = descriptor

    service = IndicatorCalculationService(
        catalog=catalog,
    )

    result = service.calculate(
        data=data,
        specification=specification,
    )

    catalog.get.assert_called_once_with(
        "test_indicator",
    )

    calculator.assert_called_once_with(
        data,
        specification,
    )

    assert result is expected_series