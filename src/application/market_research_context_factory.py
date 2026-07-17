from __future__ import annotations

import pandas as pd

from src.application.code_version_provider import (
    CodeVersionProvider,
    StaticCodeVersionProvider,
)
from src.application.market_assumption_set_builder import (
    build_assumption_set_from_market_specification,
)
from src.application.market_experiment_specification import (
    MarketExperimentSpecification,
)
from src.application.research_runtime_configuration import (
    ResearchRuntimeConfiguration,
)
from src.research.research_context import (
    ResearchContext,
)
from src.research.research_environment_builder import (
    ResearchEnvironmentBuilder,
)


class MarketResearchContextFactory:
    """
    Builds one reproducible research context for a market experiment.

    The factory does not load data and does not execute an experiment.
    It combines an already canonical fingerprinted dataset with the
    specification-derived assumption set and research environment.
    """

    def __init__(
        self,
        *,
        runtime_configuration: ResearchRuntimeConfiguration,
        code_version_provider: CodeVersionProvider | None = None,
        research_environment_builder: (
            ResearchEnvironmentBuilder | None
        ) = None,
    ) -> None:
        self._runtime_configuration = (
            runtime_configuration
        )

        self._code_version_provider = (
            code_version_provider
            or StaticCodeVersionProvider(
                runtime_configuration.code_version
            )
        )

        self._research_environment_builder = (
            research_environment_builder
            or ResearchEnvironmentBuilder()
        )

    def create(
        self,
        *,
        specification: MarketExperimentSpecification,
        market_data: pd.DataFrame,
    ) -> ResearchContext:
        assumptions = (
            build_assumption_set_from_market_specification(
                specification
            )
        )

        environment = (
            self._research_environment_builder.build(
                market_data,
                assumption_set_fingerprint=(
                    assumptions.fingerprint()
                ),
                code_version=(
                    self._code_version_provider
                    .get_code_version()
                ),
                executor_version=(
                    self._runtime_configuration.executor_version
                ),
                statistical_method_version=(
                    self._runtime_configuration
                    .statistical_method_version
                ),
                random_seed=(
                    self._runtime_configuration.random_seed
                ),
            )
        )

        return ResearchContext(
            specification=specification,
            environment=environment,
            market_data=market_data,
            assumptions=assumptions,
        )