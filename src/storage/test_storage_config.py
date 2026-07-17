from src.storage import RESEARCH_CYCLE_DATABASE_PATH


def test_research_cycle_database_has_dedicated_default_path() -> None:
    assert RESEARCH_CYCLE_DATABASE_PATH.name == "research_cycles.db"
    assert RESEARCH_CYCLE_DATABASE_PATH.parent.name == ".research_lab"

    assert ".project_memory" not in str(
        RESEARCH_CYCLE_DATABASE_PATH
    )