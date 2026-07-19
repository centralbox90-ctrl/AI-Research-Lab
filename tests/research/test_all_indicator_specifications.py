from __future__ import annotations

from src.indicators.discovery import (
    discover_indicators,
)
from src.research.specification_factory import (
    create_default_research_specification,
)


def test_default_specification_can_be_created_for_every_indicator():
    descriptors = discover_indicators()

    assert descriptors

    for descriptor in descriptors:
        specification = (
            create_default_research_specification(
                descriptor
            )
        )

        assert (
            specification.indicator.indicator_id
            == descriptor.id
        )
        assert (
            specification
            .indicator
            .indicator_version
            == descriptor.version
        )
        assert specification.output in {
            output.name
            for output
            in descriptor.research_space.outputs
        }
        assert len(specification.fingerprint) == 64