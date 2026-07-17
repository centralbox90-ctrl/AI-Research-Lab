# Project Memory --- Handoff

## Goal

Store project change history without losing previous code.

Each change preserves:

* date/time
* file path
* full old code
* full new code
* exact diff

## MVP status

Project Memory MVP technical implementation is complete.

Full automated regression suite:

`24 passed`

Confirmed end-to-end cycle:

`watcher -> SQLite -> snapshot -> replay -> restore -> diff`

## Working functionality

* file system watcher
* SQLite event storage
* project event model
* CREATED events
* MODIFIED events
* DELETED events
* MOVED events
* snapshot creation
* unique snapshot IDs using microseconds and UUID
* replay
* legacy snapshot layout support
* current snapshot layout support
* restore
* text diff
* snapshot diff
* BEFORE/AFTER/DIFF reports
* full file history
* history export
* grouping by date and file
* watcher debounce
* ignored directories
* ignored extensions
* daily history statistics
* selected-date statistics
* empty-date handling

## Important fixes

Snapshots use microseconds + UUID.

Multiple saves no longer overwrite earlier snapshots.

Replay supports old and new snapshot layouts.

Watcher has 1-second debounce.

False events from `.project_memory/events.db` and
`events.db-journal` were removed after backup.

`ProjectDatabase` accepts a custom SQLite database path.

Default production database remains:

`.project_memory/events.db`

`SnapshotEngine` accepts a custom snapshot directory and project root.

Default production snapshot directory remains:

`.project_memory/snapshots`

Dependency injection is supported by `ProjectWatcher` for:

* database
* snapshot engine

This allows isolated automated tests without modifying production
project history.

## Clean production event counts

* `src/research/question.py` --- 6
* `src/research/test_snapshot.py` --- 1
* `src/project_memory/test3.py` --- 1
* `src/project_memory/test2.py` --- 1

These counts describe the cleaned production history recorded before
the automated regression expansion.

## Automated regression tests

Full result:

`24 passed`

### History statistics

Module:

`src/project_memory/test_history_stats.py`

2 tests:

* selected-date statistics
* empty-date handling

### Replay, restore, and diff

Module:

`src/project_memory/test_replay_restore_diff.py`

6 tests:

* new snapshot layout replay
* legacy snapshot layout replay
* snapshot filtering by original file
* snapshot restore
* text diff
* snapshot diff

### Database and events

Module:

`src/project_memory/test_database_event.py`

5 tests:

* project event creation
* directory event creation
* events table creation
* file event persistence
* directory event persistence

### Watcher

Module:

`src/project_memory/test_watcher.py`

10 tests:

* `.project_memory` ignored
* Python cache ignored
* ignored extension handling
* normal Python file accepted
* duplicate event detection
* CREATED event persistence
* directory event ignored
* MODIFIED snapshot creation
* DELETED event without snapshot
* MOVED event destination path handling

### End-to-end

Module:

`src/project_memory/test_end_to_end.py`

1 test.

Confirmed complete isolated cycle:

1. create project file
2. process CREATED event
3. process first MODIFIED event
4. create first snapshot
5. modify file
6. process second MODIFIED event
7. create second snapshot
8. verify SQLite events
9. replay file snapshots
10. restore old and new content
11. generate snapshot diff
12. verify removed and added lines

## Storage safety

Snapshots are primary project memory.

Reports are derived views.

Do not delete old production snapshots.

Do not delete:

`.project_memory/events_backup_before_cleanup.db`

Automated regression tests must not modify production history.

Temporary paths and temporary SQLite databases are used for isolated
tests.

## Code modification rule

If a file must be changed, rewrite the complete file.

Do not apply partial patches.

Always provide the exact PowerShell command needed to open the file
before editing.

After replacing a file, run the relevant isolated test first.

Then run the full regression suite.

## MVP completion point

Technical MVP functionality is complete.

Current regression result:

`24 passed`

The core Project Memory cycle is confirmed end-to-end.

## Before declaring final release

Remaining release tasks:

* update `PROJECT_MEMORY_STATE.md`
* perform one manual production watcher smoke test
* verify production history after the smoke test
* run final `24 passed` regression suite
* record final MVP completion state

## Post-MVP

Not required for MVP:

* version migration
* AST/Semantic Diff
* AI Summary
* CLI cleanup

Do not start post-MVP architecture work until MVP release verification
is complete.

## Next action

Update:

`PROJECT_MEMORY_STATE.md`

Then perform the final manual MVP release verification.
