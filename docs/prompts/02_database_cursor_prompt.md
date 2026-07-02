# Cursor Prompt — EPIC 02 Database + State Machine

## Context
Use the existing foundation documents and keep the implementation within EPIC 02 only.
Inspect the current repository state before editing and preserve unrelated files.

## Source of truth
`docs/ai_lead_intake_bitrix24_tz_v1_0.md`

## Task
Define persistence and the request lifecycle state machine for the MVP.

## Files to create/change
- `app/models/*`
- `app/schemas/*`
- `app/db/*` or equivalent persistence layer
- Tests for models, enums, and state transitions
- Minimal documentation updates only if needed for the implemented schema

## Implementation constraints
- Use the states from the TЗ and keep them explicit in code.
- Keep the schema portable and straightforward to migrate later.
- Do not introduce external integrations.
- Do not touch admin UI, AI provider logic, or Bitrix adapter code.

## Non-goals
- No external integrations.
- No dashboard work.

## Acceptance criteria
- States are explicit and testable.
- Queue records persist correctly.
- State transitions are documented or encoded clearly enough to test.

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
- EPIC 03 — Intake API + Security + Idempotency
