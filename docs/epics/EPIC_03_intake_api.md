# EPIC 03 — Intake API + Security + Idempotency

## Goal
Expose a safe intake endpoint that stores requests exactly once.

## Source of truth
`docs/ai_lead_intake_bitrix24_tz_v1_0.md`

## Scope
- Protected intake endpoint.
- Input validation.
- Idempotency handling.

## Out of scope
- AI and Bitrix processing.
- Admin UI changes.

## Expected files
- Intake route handlers
- Request schemas
- Security helpers

## Implementation notes
- Keep the endpoint fast.
- Return stable responses for duplicate keys.
- Log intake events without exposing PII.

## Acceptance criteria
- Secret-protected intake works.
- Duplicates are recognized.
- Invalid payloads are rejected cleanly.

## Definition of Done
- Intake is safe, deterministic, and covered by tests.

## Cursor prompt location
`docs/prompts/03_intake_api_cursor_prompt.md`
