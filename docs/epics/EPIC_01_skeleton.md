# EPIC 01 — Skeleton + Config + Healthcheck

## Goal
Create the minimal runnable application skeleton, configuration layer, and healthcheck.

## Source of truth
`docs/ai_lead_intake_bitrix24_tz_v1_0.md`

## Scope
- Application entrypoint.
- Settings and environment loading.
- Health endpoint.

## Out of scope
- AI classifier.
- Bitrix24 adapter.
- DB queue behavior beyond skeleton wiring.

## Expected files
- `app/main.py`
- `app/config.py`
- `app/api/health.py`

## Implementation notes
- Keep the app thin and testable.
- No business logic in route handlers.
- Any new technology requires an ADR.

## Acceptance criteria
- App starts locally.
- Healthcheck responds successfully.
- Config loads predictably.

## Definition of Done
- Skeleton runs without feature code.
- Tests cover the healthcheck and config basics.

## Cursor prompt location
`docs/prompts/01_skeleton_cursor_prompt.md`
