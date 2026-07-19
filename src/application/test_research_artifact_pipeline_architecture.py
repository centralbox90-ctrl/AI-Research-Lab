from pathlib import Path


LEGACY_USE_CASES = (
    "RunResearchCycle",
    "RunAndStoreSerializedResearchCycle",
    "RunAndStoreSerializedResearchCampaign",
)


def test_production_code_does_not_use_legacy_research_persistence():
    src_path = Path(__file__).resolve().parents[1]

    excluded_files = {
        "__init__.py",
        "run_research_cycle.py",
        "run_and_store_serialized_research_cycle.py",
        "run_and_store_serialized_research_campaign.py",
    }

    violations: list[str] = []

    for python_file in src_path.rglob("*.py"):
        if python_file.name.startswith("test_"):
            continue

        if python_file.name in excluded_files:
            continue

        source = python_file.read_text(
            encoding="utf-8",
        )

        for legacy_use_case in LEGACY_USE_CASES:
            if legacy_use_case in source:
                violations.append(
                    f"{python_file}: {legacy_use_case}"
                )

    assert violations == [], (
        "Production code must use RunAndStoreResearchArtifact "
        "instead of legacy research persistence paths:\n"
        + "\n".join(violations)
    )