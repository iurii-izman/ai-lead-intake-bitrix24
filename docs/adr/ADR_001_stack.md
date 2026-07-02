# ADR 001 — Stack

## Status
Accepted

## Context
The project needs a modern but lightweight stack that supports a portfolio/demo MVP and can be extended later.

## Decision
- Python 3.12.
- FastAPI.
- SQLite for the Demo MVP.
- SQLAlchemy 2.
- Pydantic.
- Jinja2 + HTMX + Tailwind CDN.
- Docker Compose later.
- pytest.
- ruff.

## Consequences
- Fast iteration and simple local development.
- Clear upgrade path to stronger persistence and deployment later.

## Alternatives considered
- Full SPA frontend.
- Celery/Redis in the MVP.
- PostgreSQL immediately.
