from src.api import create_research_api


class StubListStoredResearchCycles:
    def __init__(
        self,
        result_ids: list[str],
    ) -> None:
        self.result_ids = result_ids
        self.calls = 0

    def execute(self) -> list[str]:
        self.calls += 1

        return list(self.result_ids)


class MissingExecute:
    pass


def test_lists_stored_research_cycles(
) -> None:
    use_case = StubListStoredResearchCycles(
        [
            "result-002",
            "result-001",
        ]
    )
    application = create_research_api(
        list_stored_research_cycles=use_case,
    )
    client = application.test_client()

    response = client.get(
        "/v1/research-cycles"
    )

    assert response.status_code == 200
    assert response.content_type == (
        "application/json"
    )
    assert response.get_json() == {
        "schema_version": 1,
        "count": 2,
        "result_ids": [
            "result-002",
            "result-001",
        ],
    }
    assert use_case.calls == 1


def test_lists_empty_research_cycle_collection(
) -> None:
    use_case = StubListStoredResearchCycles([])
    application = create_research_api(
        list_stored_research_cycles=use_case,
    )
    client = application.test_client()

    response = client.get(
        "/v1/research-cycles"
    )

    assert response.status_code == 200
    assert response.get_json() == {
        "schema_version": 1,
        "count": 0,
        "result_ids": [],
    }
    assert use_case.calls == 1


def test_rejects_invalid_application_dependency(
) -> None:
    try:
        create_research_api(
            list_stored_research_cycles=(
                MissingExecute()
            ),
        )
    except TypeError as error:
        assert str(error) == (
            "list_stored_research_cycles must "
            "provide a callable execute method"
        )
    else:
        raise AssertionError(
            "TypeError was not raised"
        )