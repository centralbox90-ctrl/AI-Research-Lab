# Project Memory --- State

Project root: `D:\AI Research Lab`

Module: `src/project_memory`

Runtime data: `.project_memory`

## MVP status

Project Memory technical MVP is complete.

Current automated regression result:

`24 passed`

Confirmed end-to-end cycle:

`watcher -> SQLite -> snapshot -> replay -> restore -> diff`

## Known modules

* `config.py`
* `database.py`
* `diff_engine.py`
* `event.py`
* `history.py`
* `replay.py`
* `restore.py`
* `service.py`
* `snapshot.py`
* `watcher.py`
* `change_report.py`
* `change_history.py`
* `history_export.py`
* `history_stats.py`

`ast_parser.py` is empty and postponed until post-MVP work.

## Storage

Events:

`.project_memory/events.db`

Snapshots:

`.project_memory/snapshots`

Reports:

`.project_memory/reports`

Database backup:

`.project_memory/events_backup_before_cleanup.db`

## Confirmed functionality

* file system watcher
* SQLite event persistence
* project event creation
* CREATED event handling
* MODIFIED event handling
* DELETED event handling
* MOVED event handling
* watcher debounce
* ignored directory handling
* ignored extension handling
* snapshot creation
* unique snapshot IDs
* replay
* legacy snapshot replay
* current snapshot replay
* snapshot filtering by original file
* restore
* text diff
* snapshot diff
* BEFORE/AFTER/DIFF reports
* full file history
* history export
* grouping by date and file
* daily history statistics
* history filtering by selected date
* empty-date handling

## Database state

`ProjectDatabase` accepts an optional database path.

Default:

`.project_memory/events.db`

Custom database paths are used by isolated tests.

The parent directory is created automatically.

The `events` table is created automatically.

Stored event fields:

* id
* timestamp
* event_type
* file_path
* is_directory

## Snapshot state

`SnapshotEngine` accepts:

* optional snapshot directory
* optional project root

Default snapshot directory:

`.project_memory/snapshots`

Default project root:

current working directory

Snapshot IDs use:

* date
* time
* microseconds
* UUID suffix

Snapshot paths preserve the original project-relative file path.

## Replay compatibility

Replay supports two layouts.

Current layout:

`snapshot_id/original/project/path`

Legacy layout:

`year/month/day/hour/minute/second/original/project/path`

Snapshots are sorted by timestamp.

Snapshots can be filtered by original file path.

## Watcher state

`ProjectWatcher` supports dependency injection for:

* database
* snapshot engine

Default production behavior remains unchanged.

Watcher debounce:

`1.0 second`

Snapshots are created only for:

`MODIFIED`

Snapshots are not created for:

* CREATED
* DELETED
* MOVED

Directory events are ignored.

Configured ignored directories and extensions are respected.

MOVED events use the destination path.

## Automated tests

Full regression result:

`24 passed`

### `test_history_stats.py`

2 tests.

### `test_replay_restore_diff.py`

6 tests.

### `test_database_event.py`

5 tests.

### `test_watcher.py`

10 tests.

### `test_end_to_end.py`

1 test.

## End-to-end verification

The isolated end-to-end test confirms:

1. temporary project creation
2. temporary SQLite database creation
3. temporary snapshot storage
4. CREATED event persistence
5. first MODIFIED event persistence
6. first snapshot creation
7. source file modification
8. second MODIFIED event persistence
9. second snapshot creation
10. SQLite event verification
11. replay of file snapshots
12. restore of old snapshot content
13. restore of new snapshot content
14. snapshot diff generation
15. removed-line verification
16. added-line verification

## Safety rules

Snapshots are primary project memory.

Reports are derived views.

Do not delete old production snapshots.

Do not delete:

`.project_memory/events_backup_before_cleanup.db`

Automated tests must not modify production history.

Use temporary paths for filesystem tests.

Use temporary SQLite databases for database tests.

## Development rule

If a source file must be changed, rewrite the complete file.

Do not apply partial patches.

Always provide the exact PowerShell command required to open a file
before editing.

After changing a file:

1. run the relevant isolated test
2. run the full regression suite

## Current development point

Technical MVP implementation is complete.

Current regression suite:

`24 passed`

Remaining MVP release verification:

* manual production watcher smoke test
* production history verification
* final regression run
* final MVP completion record

## Post-MVP

Deferred:

* version migration
* AST/Semantic Diff
* AI Summary
* CLI cleanup

Do not redesign architecture before final MVP release verification.
