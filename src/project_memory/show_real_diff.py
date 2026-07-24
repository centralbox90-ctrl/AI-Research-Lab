from src.project_memory.diff_engine import DiffEngine
from src.project_memory.replay import ReplayEngine


FILE_PATH = "src/research/question.py"


replay = ReplayEngine()

diff_engine = DiffEngine()


snapshots = replay.get_snapshots_for_file(
    FILE_PATH
)


print("=" * 70)

print(f"File: {FILE_PATH}")

print(f"Snapshots: {len(snapshots)}")

print("=" * 70)


if len(snapshots) < 2:

    print("Not enough snapshots for diff.")

    raise SystemExit


old_snapshot = snapshots[-2]

new_snapshot = snapshots[-1]


print()

print("OLD")

print(old_snapshot.timestamp)

print()

print("NEW")

print(new_snapshot.timestamp)

print()


diff = diff_engine.compare_snapshots(
    old_snapshot,
    new_snapshot,
)


print("=" * 70)

print(diff)

print("=" * 70)