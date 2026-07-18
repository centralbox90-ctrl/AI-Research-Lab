from src.application.canonical_market_data_provider import (
    CanonicalMarketDataProvider,
)
from src.application.generated_market_data_provider import (
    GeneratedMarketDataProvider,
)
from src.application.git_code_version_provider import (
    GitCodeVersionProvider,
)
from src.application.git_command_runner import (
    GitCommandRunner,
)
from src.application.market_data_provider import (
    MarketDataProvider,
)
from src.application.market_research_context_factory import (
    MarketResearchContextFactory,
)
from src.application.market_research_session_factory import (
    MarketResearchSessionFactory,
)
from src.application.market_signal_provider import (
    MarketSignalProvider,
)
from src.application.research_runtime_configuration import (
    ResearchRuntimeConfiguration,
)
from src.application.run_and_store_research_artifact import (
    RunAndStoreResearchArtifact,
)
from src.application.run_market_research import (
    RunMarketResearch,
)
from src.application.serialized_research_cycle_store import (
    SerializedResearchCycleStore,
)
from src.application.simple_market_signal_provider import (
    SimpleMarketSignalProvider,
)
from src.storage import (
    RESEARCH_CYCLE_DATABASE_PATH,
    SqliteResearchCycleStore,
)


def build_market_research_application(
    data_provider: MarketDataProvider,
    signal_provider: MarketSignalProvider,
    store: SerializedResearchCycleStore,
) -> RunMarketResearch:
    """
    Build the market-research application dependency graph.

    The application uses the reproducible session pipeline.
    """

    canonical_data_provider = CanonicalMarketDataProvider(
        provider=data_provider,
    )

    git_commit_reader = GitCommandRunner()

    code_version_provider = GitCodeVersionProvider(
        git_commit_reader=git_commit_reader,
        fallback="development",
    )

    runtime_configuration = ResearchRuntimeConfiguration(
        code_version=(
            code_version_provider.get_code_version()
    ),
        executor_version="backtest-engine:v1",
        statistical_method_version="statistics:v1",
        random_seed=42,
    )

    context_factory = MarketResearchContextFactory(
        runtime_configuration=runtime_configuration,
        code_version_provider=code_version_provider,
    )

    session_factory = MarketResearchSessionFactory(
        data_provider=canonical_data_provider,
        signal_provider=signal_provider,
        context_factory=context_factory,
    )

    run_and_store = RunAndStoreResearchArtifact(
        store=store,
    )

    return RunMarketResearch(
        run_and_store=run_and_store,
        session_factory=session_factory,
    )


def build_default_market_research_application(
) -> RunMarketResearch:
    """
    Build a ready-to-run local market research application.

    Uses generated market data, simple rule-based signals, and the
    default SQLite research-cycle store.

    Production adapters can replace these dependencies without changing
    the market-research use case.
    """

    store = SqliteResearchCycleStore(
        db_path=RESEARCH_CYCLE_DATABASE_PATH,
    )

    return build_market_research_application(
        data_provider=GeneratedMarketDataProvider(),
        signal_provider=SimpleMarketSignalProvider(),
        store=store,
    )
