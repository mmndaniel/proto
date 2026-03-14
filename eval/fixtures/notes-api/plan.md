# Plan: Note-taking API

## TASK-001: Project scaffolding
Set up FastAPI project structure with pyproject.toml, main.py entry point, and directory layout.
Dependencies: none

## TASK-002: Database layer
SQLite database with notes table (id, title, content, tags, created_at, updated_at). CRUD functions.
Dependencies: TASK-001

## TASK-003: CRUD endpoints
REST endpoints: POST /notes, GET /notes, GET /notes/{id}, PUT /notes/{id}, DELETE /notes/{id}.
Dependencies: TASK-001, TASK-002

## TASK-004: Search endpoint
GET /notes/search?q=query - full-text search across title and content.
Dependencies: TASK-002

## TASK-005: Export endpoint
GET /notes/{id}/export?format=md|pdf - export a note as Markdown or PDF.
Dependencies: TASK-002

## TASK-006: Authentication
Protect all endpoints with authentication. Only authenticated users can access their notes.
Dependencies: TASK-003
