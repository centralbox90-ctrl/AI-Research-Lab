from datetime import datetime
from pathlib import Path

from .diff_engine import DiffEngine
from .replay import ReplayEngine
from .restore import RestoreEngine


def test_replay_reads_new_snapshot_layout(
    tmp_path: Path,
) -> None:

    snapshot_dir = tmp_path / "snapshots"

    snapshot_file = (
        snapshot_dir
        / "20260713_120000_123456_abcd1234"
        / "src"
        / "example.py"
    )

    snapshot_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    snapshot_file.write_text(
        "print('new')\n",
        encoding="utf-8",
    )

    replay = ReplayEngine()
    replay.snapshot_dir = snapshot_dir

    snapshots = replay.list_snapshots()

    assert len(snapshots) == 1

    snapshot = snapshots[0]

    assert snapshot.timestamp == datetime(
        2026,
        7,
        13,
        12,
        0,
        0,
        123456,
    )

    assert snapshot.original_path == Path(
        "src/example.py"
    )

    assert snapshot.snapshot_path == snapshot_file


def test_replay_reads_legacy_snapshot_layout(
    tmp_path: Path,
) -> None:

    snapshot_dir = tmp_path / "snapshots"

    snapshot_file = (
        snapshot_dir
        / "2026"
        / "07"
        / "13"
        / "12"
        / "00"
        / "00"
        / "src"
        / "legacy.py"
    )

    snapshot_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    snapshot_file.write_text(
        "legacy = True\n",
        encoding="utf-8",
    )

    replay = ReplayEngine()
    replay.snapshot_dir = snapshot_dir

    snapshots = replay.list_snapshots()

    assert len(snapshots) == 1

    snapshot = snapshots[0]

    assert snapshot.timestamp == datetime(
        2026,
        7,
        13,
        12,
        0,
        0,
    )

    assert snapshot.original_path == Path(
        "src/legacy.py"
    )


def test_get_snapshots_for_file(
    tmp_path: Path,
) -> None:

    snapshot_dir = tmp_path / "snapshots"

    first = (
        snapshot_dir
        / "20260713_120000_000001_first001"
        / "src"
        / "example.py"
    )

    second = (
        snapshot_dir
        / "20260713_120001_000002_second02"
        / "src"
        / "other.py"
    )

    first.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    second.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    first.write_text(
        "first\n",
        encoding="utf-8",
    )

    second.write_text(
        "second\n",
        encoding="utf-8",
    )

    replay = ReplayEngine()
    replay.snapshot_dir = snapshot_dir

    snapshots = replay.get_snapshots_for_file(
        "src/example.py"
    )

    assert len(snapshots) == 1
    assert snapshots[0].snapshot_path == first


def test_restore_reads_snapshot(
    tmp_path: Path,
) -> None:

    snapshot_file = tmp_path / "snapshot.py"

    snapshot_file.write_text(
        "value = 42\n",
        encoding="utf-8",
    )

    from .replay import SnapshotInfo

    snapshot = SnapshotInfo(
        timestamp=datetime(
            2026,
            7,
            13,
            12,
            0,
        ),
        original_path=Path("src/example.py"),
        snapshot_path=snapshot_file,
    )

    restore = RestoreEngine()

    assert restore.read_snapshot(snapshot) == (
        "value = 42\n"
    )


def test_diff_compares_text() -> None:

    diff_engine = DiffEngine()

    result = diff_engine.compare_text(
        "value = 1\n",
        "value = 2\n",
    )

    assert "--- OLD" in result
    assert "+++ NEW" in result
    assert "-value = 1" in result
    assert "+value = 2" in result


def test_diff_compares_snapshots(
    tmp_path: Path,
) -> None:

    old_file = tmp_path / "old.py"
    new_file = tmp_path / "new.py"

    old_file.write_text(
        "name = 'old'\n",
        encoding="utf-8",
    )

    new_file.write_text(
        "name = 'new'\n",
        encoding="utf-8",
    )

    from .replay import SnapshotInfo

    old_snapshot = SnapshotInfo(
        timestamp=datetime(
            2026,
            7,
            13,
            12,
            0,
        ),
        original_path=Path("src/example.py"),
        snapshot_path=old_file,
    )

    new_snapshot = SnapshotInfo(
        timestamp=datetime(
            2026,
            7,
            13,
            12,
            1,
        ),
        original_path=Path("src/example.py"),
        snapshot_path=new_file,
    )

    result = DiffEngine().compare_snapshots(
        old_snapshot,
        new_snapshot,
    )

    assert "-name = 'old'" in result
    assert "+name = 'new'" in result