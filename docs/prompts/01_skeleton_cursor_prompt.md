# Cursor Prompt — EPIC 01 Skeleton + Config + Healthcheck

## Context
You are working in `C:\dev_bitrix24\ai_lead_intake_bitrix24`.
Inspect the current repository state before editing and keep the work within the files listed below.

## Source of truth
`docs/ai_lead_intake_bitrix24_tz_v1_0.md`

## Task
Create the minimal application skeleton, settings layer, and healthcheck endpoint only.

## Files to create/change
- `app/main.py`
- `app/config.py`
- `app/api/health.py`
- `app/__init__.py` if needed
- `app/api/__init__.py` if needed
- `tests/__init__.py` if needed
- Any minimal support files required for imports and tests

## Implementation constraints
- Keep the app thin and importable.
- Prefer a single FastAPI application object and a single health route.
- Do not add database, AI, Bitrix24, or worker logic.
- Do not modify docs, ADRs, or prompts.

## Non-goals
- No database models.
- No intake API.
- No AI classifier.
- No Bitrix24 adapter.

## Acceptance criteria
- The app starts.
- `/health` returns a healthy response.
- Config values load from environment cleanly.
- The implementation is limited to the skeleton scope.

## Final report format
## Done
- ...

## Files changed
- ...

## How to verify
- ...

## Notes / assumptions
- ...

## Next step
- EPIC 02 — Database + State Machine
