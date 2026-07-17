from src.project_memory.replay import ReplayEngine
from src.project_memory.restore import RestoreEngine


replay = ReplayEngine()

restore = RestoreEngine()

snapshots = replay.list_snapshots()

if not snapshots:

    print("Snapshot not found")

    raise SystemExit


text = restore.read_snapshot(
    snapshots[-1]
)

print("=" * 60)

print(text)

print("=" * 60)