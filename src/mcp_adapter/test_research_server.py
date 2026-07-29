import pytest
from mcp import Client

from src.mcp_adapter import (
    create_research_mcp_server,
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
        get_stored_research_artifact=(
            StubGetStoredResearchArtifact(None)
        ),
        list_stored_research_cycles=(
            StubListStoredResearchCycles([])
        ),
    )

    tools = await server.list_tools()

    assert len(tools) == 2

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

    assert len(tools) == 2
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
            get_stored_research_artifact=(
                MissingExecute()
            ),
            list_stored_research_cycles=(
                StubListStoredResearchCycles([])
            ),
        )
