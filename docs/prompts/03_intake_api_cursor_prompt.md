# Cursor Prompt — EPIC 03 Intake API + Security + Idempotency

## Context
Implement a safe intake path that accepts requests exactly once.
Inspect the existing repository state first and keep changes scoped to the intake path.

## Source of truth
`docs/ai_lead_intake_bitrix24_tz_v1_0.md`

## Task
Build the protected intake endpoint with validation and idempotency.

## Files to create/change
- `app/api/intake.py` or equivalent route module
- Intake request/response schemas
- Webhook secret and idempotency helpers
- Tests for success, duplicate, secret failure, and payload validation

## Implementation constraints
- Reject unauthorized requests before any persistence or business logic.
- Return stable responses for duplicate idempotency keys.
- Mask sensitive payload details in logs.
- Do not invoke AI or Bitrix24 from this epic.

## Non-goals
- No AI classification.
- No Bitrix synchronization.

## Acceptance criteria
- Valid requests are accepted.
- Invalid secrets are rejected.
- Duplicate keys resolve to the existing record.
- No out-of-scope processing is introduced.

## Final report format
## Done
- ...

## Files changed
- ...

## Branch / commit / PR
- Branch:
- Commit:
- Push:
- PR:

## How to verify
- ...

## Notes / assumptions
- ...

## Tree state
- Working tree is clean at the end of the epic.

## Next step
- EPIC 04 — AI Classifier
