# Cursor Prompt — EPIC 09 Tests + Security

## Context
The core app exists; now harden behavior with tests and security checks.
Inspect the current repository state first and keep the test changes aligned with the codebase.

## Source of truth
`docs/ai_lead_intake_bitrix24_tz_v1_0.md`

## Task
Add unit, integration, and security tests for the critical flows.

## Files to create/change
- `tests/*`
- Test helpers and fixtures
- Security-focused tests for auth, secret handling, and masking
- Any minimal test config needed to run pytest cleanly

## Implementation constraints
- No real external network calls in tests.
- Mock AI and Bitrix24.
- Keep tests deterministic and fast.
- Do not expand product scope through tests.

## Non-goals
- No new product features.

## Acceptance criteria
- Tests cover the critical flows and edge cases.
- No real network calls are used.
- Security behavior is covered by explicit assertions.

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
- EPIC 10 — Portfolio Packaging
