# EPIC 02 — Database + State Machine

## Goal
Define persistence, queue records, and explicit request lifecycle states.

## Source of truth
`docs/ai_lead_intake_bitrix24_tz_v1_0.md`

## Scope
- Queue tables and related entities.
- State machine definitions.
- Repository layer boundaries.

## Out of scope
- External integrations.
- Dashboard polish.

## Expected files
- Database models
- Schema documentation
- State machine tests

## Implementation notes
- State transitions must be deterministic.
- Keep schema portable for later PostgreSQL migration.
- Do not expand scope without ADR updates.

## Acceptance criteria
- States are documented and enforced.
- Queue records can be created and updated safely.

## Definition of Done
- Persistence design is testable and aligned with the TЗ.

## Cursor prompt location
`docs/prompts/02_database_cursor_prompt.md`
