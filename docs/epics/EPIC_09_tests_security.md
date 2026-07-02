# EPIC 09 — Tests + Security

## Goal
Prove core behavior and enforce security constraints.

## Source of truth
`docs/ai_lead_intake_bitrix24_tz_v1_0.md`

## Scope
- Unit tests.
- Integration tests.
- Security-related checks.

## Out of scope
- New product features.

## Expected files
- pytest suite
- Security tests
- Test helpers

## Implementation notes
- No real network calls.
- Mock OpenAI and Bitrix24.
- Cover failure and edge cases.
- Any test-only request for new runtime behavior should be captured as an ADR or explicit scope change.

## Acceptance criteria
- Tests pass cleanly and cover the critical flows.

## Definition of Done
- Security behavior and core flows are both validated.
- Tests run without external dependencies.

## Cursor prompt location
`docs/prompts/09_tests_security_cursor_prompt.md`
