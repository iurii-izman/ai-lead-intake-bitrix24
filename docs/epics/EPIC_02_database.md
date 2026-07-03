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
- Any model or migration decision outside this epic requires an ADR before implementation.

## Acceptance criteria
- States are documented and enforced.
- Queue records can be created and updated safely.

## Definition of Done
- Persistence design is testable and aligned with the TЗ.
- The state machine is explicit and reviewable.
- Changes are committed, pushed, and handed off via a draft PR unless the user explicitly requests a direct main push.
- Working tree is clean at handoff.

## Actual completion status

Status: complete in the current repository baseline.

Implemented:
- SQLAlchemy models for the core tables.
- request status enum and centralized lifecycle transitions.
- DB initialization path for the demo MVP.
- model/schema/state-machine tests.

If this epic is revisited, audit and refine the existing persistence layer instead of recreating it.

## Cursor prompt location
`docs/prompts/02_database_cursor_prompt.md`
