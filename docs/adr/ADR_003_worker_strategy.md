# ADR 003 — Worker Strategy

## Status
Accepted

## Context
The first delivery needs asynchronous processing without introducing unnecessary infrastructure.

## Decision
- Use a DB queue plus an in-process worker for the Demo MVP.
- Do not use Celery or Redis in the MVP.
- Keep the design replaceable by an external queue later.

## Consequences
- Less operational overhead in the first release.
- Easy to demonstrate the pipeline end to end.

## Alternatives considered
- Celery with Redis.
- Managed queue services.
