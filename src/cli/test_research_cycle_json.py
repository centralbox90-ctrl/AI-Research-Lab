import json

from src.cli import ResearchCycleJsonPresenter


def test_research_cycle_json_presenter_renders_adapter_safe_data() -> None:
    serialized_cycle = {
        "result": {
            "id": "result-001",
            "success": True,
        },
        "evidence_strength_evaluation": {
            "level": "very_strong",
            "score": 1.0,
        },
        "hypothesis_decision": {
            "is_supported": True,
        },
        "next_experiment_selection": {
            "action": "replicate_experiment",
        },
        "conclusion": {
            "statement": "Гипотеза поддержана.",
            "supported": True,
        },
    }

    presenter = ResearchCycleJsonPresenter()

    rendered = presenter.render(serialized_cycle)

    parsed = json.loads(rendered)

    assert parsed == serialized_cycle
    assert parsed["result"]["id"] == "result-001"
    assert parsed["hypothesis_decision"]["is_supported"] is True
    assert (
        parsed["next_experiment_selection"]["action"]
        == "replicate_experiment"
    )

    assert "Гипотеза поддержана." in rendered
    assert "\\u0413" not in rendered


def test_research_cycle_json_presenter_supports_compact_output() -> None:
    presenter = ResearchCycleJsonPresenter()

    rendered = presenter.render(
        {
            "result": {
                "id": "result-002",
            },
        },
        indent=None,
    )

    assert json.loads(rendered)["result"]["id"] == "result-002"
    assert "\n" not in rendered