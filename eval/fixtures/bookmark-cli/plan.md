# Plan: bookmark-cli

## TASK-001: Project scaffolding
Python package structure, pyproject.toml, argparse CLI with add/list/search subcommands (stubs), entry point.
Dependencies: none

## TASK-002: Database layer
SQLite CRUD: init_db, add_bookmark, list_bookmarks, search_bookmarks. Store at ~/.bookmarks.db.
Dependencies: none

## TASK-003: Add command
Wire up the add subcommand to call db.add_bookmark. Args: url, --title, --tags, --notes.
Dependencies: TASK-001, TASK-002

## TASK-004: List command
Wire up list subcommand with --format (text/table/json) and --recent. Create formatters module.
Dependencies: TASK-001, TASK-002

## TASK-005: Search command
Wire up search subcommand to call db.search_bookmarks and display results.
Dependencies: TASK-001, TASK-002
