# Cursor Prompt — EPIC 09 Tests + Security

## Context
The core app exists; now harden behavior with tests and security checks.
Inspect the current repository state first and keep the test changes aligned with the codebase.
This epic is already implemented in the repository baseline.

## Source of truth
`docs/ai_lead_intake_bitrix24_tz_v1_0.md`

## Task
Audit the existing test and security baseline.
Add or adjust tests only for verified gaps, regressions, or missing hardening checks.

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
- The suite remains deterministic and locally green.

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
- EPIC 10 — Portfolio Packaging
