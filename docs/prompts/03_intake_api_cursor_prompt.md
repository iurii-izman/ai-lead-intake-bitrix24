# Cursor Prompt — EPIC 03 Intake API + Security + Idempotency

## Context
Implement a safe intake path that accepts requests exactly once.

## Source of truth
`docs/ai_lead_intake_bitrix24_tz_v1_0.md`

## Task
Build the protected intake endpoint with validation and idempotency.

## Files to create/change
- Intake route handlers
- Request schema
- Security and duplicate-check helpers

## Non-goals
- No AI classification.
- No Bitrix synchronization.

## Acceptance criteria
- Valid requests are accepted.
- Invalid secrets are rejected.
- Duplicate keys resolve to the existing record.

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
- EPIC 04 — AI Classifier
