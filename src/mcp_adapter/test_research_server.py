import pytest
from mcp import Client

from src.application.artifact_comparison_factory import (
    ArtifactComparisonFactory,
)
from src.application.public_api import (
    StoredResearchArtifactIntegrityError,
)
from src.mcp_adapter import (
    create_research_mcp_server,
)


class StubCompareStoredResearchArtifacts:
    def __init__(
        self,
        error: ValueError | None = None,
    ) -> None:
        self.error = error
        self.calls: list[tuple[str, str]] = []

    def execute(
        self,
        artifact_a_result_id: str,
        artifact_b_result_id: str,
    ):
        self.calls.append(
            (
                artifact_a_result_id,
                artifact_b_result_id,
            )
        )

        if self.error is not None:
            raise self.error

        return ArtifactComparisonFactory().create(
            artifact_a_id="artifact-001",
            artifact_b_id="artifact-002",
            previous_hypothesis="Previous hypothesis",
            current_hypothesis="Current hypothesis",
            hypothesis_change_reason=(
                "Hypothesis changed."
            ),
            previous_evidence={
                "net_profit": 1.0,
            },
            current_evidence={
                "net_profit": 2.5,
            },
            evidence_change_reason=(
                "Evidence changed."
            ),
            previous_confidence=0.4,
            current_confidence=0.7,
            confidence_change_reason=(
                "Confidence increased."
            ),
        )


class StubListStoredResearchCycles:
    def __init__(
        self,
        result_ids: object,
    ) -> None:
        self.result_ids = result_ids
        self.calls = 0

    def execute(self):
        self.calls += 1

        return self.result_ids


class StubGetStoredResearchArtifact:
    def __init__(
        self,
        artifact: object,
    ) -> None:
        self.artifact = artifact
        self.calls: list[str] = []

    def execute(
        self,
        result_id: str,
    ):
        self.calls.append(result_id)

        return self.artifact


class FailingGetStoredResearchArtifact:
    def execute(
        self,
        result_id: str,
    ):
        raise StoredResearchArtifactIntegrityError(
            result_id=result_id,
            reason="payload fingerprint mismatch",
        )


class FailingListStoredResearchCycles:
    def execute(self):
        raise StoredResearchArtifactIntegrityError(
            result_id="result-corrupt",
            reason="storage identity mismatch",
        )


class MissingExecute:
    pass


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.anyio
async def test_lists_research_cycles_through_mcp(
) -> None:
    use_case = StubListStoredResearchCycles(
        [
            "result-002",
            "result-001",
        ]
    )
    server = create_research_mcp_server(
        compare_stored_research_artifacts=(
            StubCompareStoredResearchArtifacts()
        ),
        get_stored_research_artifact=(
            StubGetStoredResearchArtifact(None)
        ),
        list_stored_research_cycles=use_case,
    )

    async with Client(
        server,
        raise_exceptions=True,
    ) as client:
        result = await client.call_tool(
            "list_research_cycles",
            {},
        )

    assert result.is_error is False
    assert result.structured_content == {
        "schema_version": 1,
        "count": 2,
        "result_ids": [
            "result-002",
            "result-001",
        ],
    }
    assert use_case.calls == 1


@pytest.mark.anyio
async def test_publishes_read_only_tool_contract(
) -> None:
    server = create_research_mcp_server(
        compare_stored_research_artifacts=(
            StubCompareStoredResearchArtifacts()
        ),
        get_stored_research_artifact=(
            StubGetStoredResearchArtifact(None)
        ),
        list_stored_research_cycles=(
            StubListStoredResearchCycles([])
        ),
    )

    tools = await server.list_tools()

    assert len(tools) == 3

    tool = tools[0]

    assert tool.name == "list_research_cycles"
    assert tool.title == "List research cycles"
    assert tool.input_schema == {
        "properties": {},
        "title": (
            "list_research_cyclesArguments"
        ),
        "type": "object",
    }
    assert tool.output_schema is not None
    assert tool.annotations is not None
    assert tool.annotations.read_only_hint is True
    assert tool.annotations.destructive_hint is False
    assert tool.annotations.idempotent_hint is True
    assert tool.annotations.open_world_hint is False


@pytest.mark.anyio
async def test_reports_invalid_application_result(
) -> None:
    use_case = StubListStoredResearchCycles(
        (
            "result-001",
        )
    )
    server = create_research_mcp_server(
        compare_stored_research_artifacts=(
            StubCompareStoredResearchArtifacts()
        ),
        get_stored_research_artifact=(
            StubGetStoredResearchArtifact(None)
        ),
        list_stored_research_cycles=use_case,
    )

    async with Client(
        server,
        raise_exceptions=True,
    ) as client:
        result = await client.call_tool(
            "list_research_cycles",
            {},
        )

    assert result.is_error is True
    assert result.content
    assert (
        "ListStoredResearchCycles must return a list"
        in result.content[0].text
    )
    assert use_case.calls == 1


def test_rejects_invalid_application_dependency(
) -> None:
    with pytest.raises(
        TypeError,
        match=(
            "list_stored_research_cycles must "
            "provide a callable execute method"
        ),
    ):
        create_research_mcp_server(
            compare_stored_research_artifacts=(
                StubCompareStoredResearchArtifacts()
            ),
            get_stored_research_artifact=(
                StubGetStoredResearchArtifact(None)
            ),
            list_stored_research_cycles=(
                MissingExecute()
            ),
        )


@pytest.mark.anyio
async def test_gets_research_artifact_through_mcp(
) -> None:
    artifact = {
        "artifact_type": "market_research",
        "result": {
            "id": "result-001",
        },
    }
    use_case = StubGetStoredResearchArtifact(
        artifact
    )
    server = create_research_mcp_server(
        compare_stored_research_artifacts=(
            StubCompareStoredResearchArtifacts()
        ),
        get_stored_research_artifact=use_case,
        list_stored_research_cycles=(
            StubListStoredResearchCycles([])
        ),
    )

    async with Client(
        server,
        raise_exceptions=True,
    ) as client:
        result = await client.call_tool(
            "get_research_artifact",
            {
                "result_id": "  result-001  ",
            },
        )

    assert result.is_error is False
    assert result.structured_content == {
        "schema_version": 1,
        "result_id": "result-001",
        "artifact": artifact,
    }
    assert use_case.calls == ["result-001"]


@pytest.mark.anyio
async def test_reports_missing_research_artifact(
) -> None:
    use_case = StubGetStoredResearchArtifact(None)
    server = create_research_mcp_server(
        compare_stored_research_artifacts=(
            StubCompareStoredResearchArtifacts()
        ),
        get_stored_research_artifact=use_case,
        list_stored_research_cycles=(
            StubListStoredResearchCycles([])
        ),
    )

    async with Client(
        server,
        raise_exceptions=True,
    ) as client:
        result = await client.call_tool(
            "get_research_artifact",
            {
                "result_id": "result-missing",
            },
        )

    assert result.is_error is True
    assert result.content
    assert (
        "Research artifact not found: result-missing"
        in result.content[0].text
    )
    assert use_case.calls == ["result-missing"]


@pytest.mark.anyio
async def test_publishes_research_artifact_tool_contract(
) -> None:
    server = create_research_mcp_server(
        compare_stored_research_artifacts=(
            StubCompareStoredResearchArtifacts()
        ),
        get_stored_research_artifact=(
            StubGetStoredResearchArtifact(None)
        ),
        list_stored_research_cycles=(
            StubListStoredResearchCycles([])
        ),
    )

    tools = await server.list_tools()
    tool = next(
        candidate
        for candidate in tools
        if candidate.name == "get_research_artifact"
    )

    assert len(tools) == 3
    assert tool.title == "Get research artifact"
    assert "result_id" in tool.input_schema[
        "properties"
    ]
    assert tool.output_schema is not None
    assert tool.annotations is not None
    assert tool.annotations.read_only_hint is True
    assert tool.annotations.destructive_hint is False
    assert tool.annotations.idempotent_hint is True
    assert tool.annotations.open_world_hint is False


def test_rejects_invalid_artifact_dependency(
) -> None:
    with pytest.raises(
        TypeError,
        match=(
            "get_stored_research_artifact must "
            "provide a callable execute method"
        ),
    ):
        create_research_mcp_server(
            compare_stored_research_artifacts=(
                StubCompareStoredResearchArtifacts()
            ),
            get_stored_research_artifact=(
                MissingExecute()
            ),
            list_stored_research_cycles=(
                StubListStoredResearchCycles([])
            ),
        )
@pytest.mark.anyio
async def test_compares_research_artifacts_through_mcp(
) -> None:
    use_case = StubCompareStoredResearchArtifacts()
    server = create_research_mcp_server(
        compare_stored_research_artifacts=use_case,
        get_stored_research_artifact=(
            StubGetStoredResearchArtifact(None)
        ),
        list_stored_research_cycles=(
            StubListStoredResearchCycles([])
        ),
    )

    async with Client(
        server,
        raise_exceptions=True,
    ) as client:
        result = await client.call_tool(
            "compare_research_artifacts",
            {
                "artifact_a_result_id": "  result-001  ",
                "artifact_b_result_id": "  result-002  ",
            },
        )

    assert result.is_error is False
    assert use_case.calls == [
        (
            "result-001",
            "result-002",
        ),
    ]

    payload = result.structured_content

    assert payload is not None
    assert payload["schema_version"] == 1
    assert payload["artifact_a_result_id"] == (
        "result-001"
    )
    assert payload["artifact_b_result_id"] == (
        "result-002"
    )
    assert payload["comparison"]["artifact_a_id"] == (
        "artifact-001"
    )
    assert (
        payload["comparison"]
        ["confidence_evolution"]
        ["current_confidence"]
        == 0.7
    )
    assert (
        payload["comparison"]
        ["evidence_evolution"]
        ["metric_deltas"][0]
        ["absolute_delta"]
        == 1.5
    )


@pytest.mark.anyio
async def test_reports_comparison_application_error(
) -> None:
    use_case = StubCompareStoredResearchArtifacts(
        ValueError(
            "Research artifact was not found "
            "for result_id: result-404"
        )
    )
    server = create_research_mcp_server(
        compare_stored_research_artifacts=use_case,
        get_stored_research_artifact=(
            StubGetStoredResearchArtifact(None)
        ),
        list_stored_research_cycles=(
            StubListStoredResearchCycles([])
        ),
    )

    async with Client(
        server,
        raise_exceptions=True,
    ) as client:
        result = await client.call_tool(
            "compare_research_artifacts",
            {
                "artifact_a_result_id": "result-001",
                "artifact_b_result_id": "result-404",
            },
        )

    assert result.is_error is True
    assert result.content
    assert (
        "Research artifact was not found "
        "for result_id: result-404"
        in result.content[0].text
    )


@pytest.mark.anyio
async def test_publishes_artifact_comparison_tool_contract(
) -> None:
    server = create_research_mcp_server(
        compare_stored_research_artifacts=(
            StubCompareStoredResearchArtifacts()
        ),
        get_stored_research_artifact=(
            StubGetStoredResearchArtifact(None)
        ),
        list_stored_research_cycles=(
            StubListStoredResearchCycles([])
        ),
    )

    tools = await server.list_tools()
    tool = next(
        candidate
        for candidate in tools
        if candidate.name == "compare_research_artifacts"
    )

    assert len(tools) == 3
    assert tool.title == "Compare research artifacts"
    assert "artifact_a_result_id" in tool.input_schema[
        "properties"
    ]
    assert "artifact_b_result_id" in tool.input_schema[
        "properties"
    ]
    assert tool.output_schema is not None
    assert tool.annotations is not None
    assert tool.annotations.read_only_hint is True
    assert tool.annotations.destructive_hint is False
    assert tool.annotations.idempotent_hint is True
    assert tool.annotations.open_world_hint is False


def test_rejects_invalid_comparison_dependency(
) -> None:
    with pytest.raises(
        TypeError,
        match=(
            "compare_stored_research_artifacts must "
            "provide a callable execute method"
        ),
    ):
        create_research_mcp_server(
            compare_stored_research_artifacts=(
                MissingExecute()
            ),
            get_stored_research_artifact=(
                StubGetStoredResearchArtifact(None)
            ),
            list_stored_research_cycles=(
                StubListStoredResearchCycles([])
            ),
        )


@pytest.mark.anyio
async def test_reports_listing_integrity_error_through_mcp(
) -> None:
    server = create_research_mcp_server(
        compare_stored_research_artifacts=(
            StubCompareStoredResearchArtifacts()
        ),
        get_stored_research_artifact=(
            StubGetStoredResearchArtifact(None)
        ),
        list_stored_research_cycles=(
            FailingListStoredResearchCycles()
        ),
    )

    async with Client(
        server,
        raise_exceptions=True,
    ) as client:
        result = await client.call_tool(
            "list_research_cycles",
            {},
        )

    assert result.is_error is True
    assert result.content
    assert (
        "stored research artifact 'result-corrupt' "
        "failed integrity validation: "
        "storage identity mismatch"
        in result.content[0].text
    )


@pytest.mark.anyio
async def test_reports_artifact_integrity_error_through_mcp(
) -> None:
    server = create_research_mcp_server(
        compare_stored_research_artifacts=(
            StubCompareStoredResearchArtifacts()
        ),
        get_stored_research_artifact=(
            FailingGetStoredResearchArtifact()
        ),
        list_stored_research_cycles=(
            StubListStoredResearchCycles([])
        ),
    )

    async with Client(
        server,
        raise_exceptions=True,
    ) as client:
        result = await client.call_tool(
            "get_research_artifact",
            {
                "result_id": "result-corrupt",
            },
        )

    assert result.is_error is True
    assert result.content
    assert (
        "stored research artifact 'result-corrupt' "
        "failed integrity validation: "
        "payload fingerprint mismatch"
        in result.content[0].text
    )
