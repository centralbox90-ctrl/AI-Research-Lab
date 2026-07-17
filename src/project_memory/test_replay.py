from src.project_memory.replay import ReplayEngine

engine = ReplayEngine()

snapshots = engine.list_snapshots()

print("=" * 60)

print(f"Snapshots: {len(snapshots)}")

print("=" * 60)

for snapshot in snapshots:

    print()

    print(snapshot.timestamp)

    print(snapshot.original_path)

    print(snapshot.snapshot_path)