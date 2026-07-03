# EPIC 03 — Intake API + Security + Idempotency

## Goal
Expose a safe intake endpoint that stores requests exactly once.

## Source of truth
`docs/ai_lead_intake_bitrix24_tz_v1_0.md`

## Scope
- Protected intake endpoint.
- Input validation.
- Idempotency handling.
- Intake rate limiting.

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
- Keep rate limiting separate from business logic so the endpoint stays thin.
- Any new request-shape or auth requirement outside the epic must be recorded in an ADR first.

## Acceptance criteria
- Secret-protected intake works.
- Duplicates are recognized.
- Invalid payloads are rejected cleanly.
- Rate limit returns `429` without creating new records.

## Definition of Done
- Intake is safe, deterministic, and covered by tests.
- Out-of-scope processing is not mixed into the endpoint.
- Changes are committed, pushed, and handed off via a draft PR unless the user explicitly requests a direct main push.
- Working tree is clean at handoff.

## Cursor prompt location
`docs/prompts/03_intake_api_cursor_prompt.md`
