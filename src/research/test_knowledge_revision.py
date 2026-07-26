from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone

import pytest

from src.research.knowledge_item import KnowledgeItem
from src.research.knowledge_revision import (
    KnowledgeRevision,
)


def build_item(
    *,
    version: int = 1,
) -> KnowledgeItem:
    return KnowledgeItem(
        id="knowledge-momentum",
        statement=(
            "Momentum persists in liquid trend regimes."
        ),
        confidence=0.85,
        applicability=(
            "liquid equity indices",
        ),
        limitations=(
            "not evaluated in crisis regimes",
        ),
        supporting_findings=(
            "finding-a",
            "finding-b",
        ),
        version=version,
        provenance=(
            (
                "knowledge_candidate_id",
                "candidate-momentum",
            ),
        ),
    )


def test_creates_initial_revision_in_utc() -> None:
    source_timezone = timezone(
        timedelta(hours=2)
    )

    revision = KnowledgeRevision(
        item=build_item(),
        valid_from=datetime(
            2026,
            7,
            26,
            12,
            30,
            tzinfo=source_timezone,
        ),
        change_reason="  Initial validation  ",
        supersedes_version=None,
    )

    assert revision.valid_from == datetime(
        2026,
        7,
        26,
        10,
        30,
        tzinfo=timezone.utc,
    )
    assert revision.change_reason == (
        "Initial validation"
    )
    assert revision.supersedes_version is None


def test_creates_sequential_revision() -> None:
    revision = KnowledgeRevision(
        item=build_item(version=2),
        valid_from=datetime(
            2026,
            7,
            27,
            tzinfo=timezone.utc,
        ),
        change_reason="New supporting findings",
        supersedes_version=1,
    )

    assert revision.item.version == 2
    assert revision.supersedes_version == 1


def test_serializes_revision_with_item_fingerprint(
) -> None:
    item = build_item()
    revision = KnowledgeRevision(
        item=item,
        valid_from=datetime(
            2026,
            7,
            26,
            10,
            30,
            tzinfo=timezone.utc,
        ),
        change_reason="Initial validation",
        supersedes_version=None,
    )

    assert revision.to_dict() == {
        "schema_version": 1,
        "item": item.to_dict(),
        "item_fingerprint": item.fingerprint,
        "valid_from": "2026-07-26T10:30:00Z",
        "change_reason": "Initial validation",
        "supersedes_version": None,
    }


def test_fingerprint_is_timezone_deterministic(
) -> None:
    item = build_item()
    utc_revision = KnowledgeRevision(
        item=item,
        valid_from=datetime(
            2026,
            7,
            26,
            10,
            30,
            tzinfo=timezone.utc,
        ),
        change_reason="Initial validation",
        supersedes_version=None,
    )
    offset_revision = KnowledgeRevision(
        item=item,
        valid_from=datetime(
            2026,
            7,
            26,
            12,
            30,
            tzinfo=timezone(
                timedelta(hours=2)
            ),
        ),
        change_reason=" Initial validation ",
        supersedes_version=None,
    )

    assert utc_revision == offset_revision
    assert (
        utc_revision.fingerprint
        == offset_revision.fingerprint
    )
    assert len(utc_revision.fingerprint) == 64


def test_revision_is_immutable() -> None:
    revision = KnowledgeRevision(
        item=build_item(),
        valid_from=datetime(
            2026,
            7,
            26,
            tzinfo=timezone.utc,
        ),
        change_reason="Initial validation",
        supersedes_version=None,
    )

    with pytest.raises(FrozenInstanceError):
        revision.change_reason = (  # type: ignore[misc]
            "Changed"
        )


def test_rejects_non_knowledge_item() -> None:
    with pytest.raises(
        TypeError,
        match="item must be a KnowledgeItem",
    ):
        KnowledgeRevision(
            item=object(),  # type: ignore[arg-type]
            valid_from=datetime(
                2026,
                7,
                26,
                tzinfo=timezone.utc,
            ),
            change_reason="Initial validation",
            supersedes_version=None,
        )


def test_rejects_non_datetime_valid_from() -> None:
    with pytest.raises(
        TypeError,
        match="valid_from must be a datetime",
    ):
        KnowledgeRevision(
            item=build_item(),
            valid_from="2026-07-26",  # type: ignore[arg-type]
            change_reason="Initial validation",
            supersedes_version=None,
        )


def test_rejects_naive_valid_from() -> None:
    with pytest.raises(
        ValueError,
        match="valid_from must be timezone-aware",
    ):
        KnowledgeRevision(
            item=build_item(),
            valid_from=datetime(
                2026,
                7,
                26,
            ),
            change_reason="Initial validation",
            supersedes_version=None,
        )


@pytest.mark.parametrize(
    "change_reason",
    (
        "",
        "   ",
    ),
)
def test_rejects_empty_change_reason(
    change_reason: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="change_reason must not be empty",
    ):
        KnowledgeRevision(
            item=build_item(),
            valid_from=datetime(
                2026,
                7,
                26,
                tzinfo=timezone.utc,
            ),
            change_reason=change_reason,
            supersedes_version=None,
        )


def test_rejects_non_string_change_reason(
) -> None:
    with pytest.raises(
        TypeError,
        match="change_reason must be a string",
    ):
        KnowledgeRevision(
            item=build_item(),
            valid_from=datetime(
                2026,
                7,
                26,
                tzinfo=timezone.utc,
            ),
            change_reason=1,  # type: ignore[arg-type]
            supersedes_version=None,
        )


def test_initial_revision_rejects_supersedes_version(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "initial revision must not "
            "supersede another version"
        ),
    ):
        KnowledgeRevision(
            item=build_item(),
            valid_from=datetime(
                2026,
                7,
                26,
                tzinfo=timezone.utc,
            ),
            change_reason="Initial validation",
            supersedes_version=1,
        )


@pytest.mark.parametrize(
    "supersedes_version",
    (
        None,
        1,
        3,
    ),
)
def test_later_revision_requires_immediate_predecessor(
    supersedes_version: int | None,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "revision must supersede the "
            "immediately preceding version"
        ),
    ):
        KnowledgeRevision(
            item=build_item(version=3),
            valid_from=datetime(
                2026,
                7,
                28,
                tzinfo=timezone.utc,
            ),
            change_reason="Updated evidence",
            supersedes_version=supersedes_version,
        )


@pytest.mark.parametrize(
    ("supersedes_version", "expected_exception"),
    (
        (True, TypeError),
        (1.5, TypeError),
        ("1", TypeError),
        (0, ValueError),
        (-1, ValueError),
    ),
)
def test_rejects_invalid_supersedes_version(
    supersedes_version: object,
    expected_exception: type[Exception],
) -> None:
    with pytest.raises(expected_exception):
        KnowledgeRevision(
            item=build_item(version=2),
            valid_from=datetime(
                2026,
                7,
                27,
                tzinfo=timezone.utc,
            ),
            change_reason="Updated evidence",
            supersedes_version=supersedes_version,  # type: ignore[arg-type]
        )
