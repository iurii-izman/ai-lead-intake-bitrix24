# Cursor Prompt — EPIC 01 Skeleton + Config + Healthcheck

## Context
You are working in `C:\dev_bitrix24\ai_lead_intake_bitrix24`.
Inspect the current repository state before editing.
This epic is already implemented in the repository baseline.

## Source of truth
`docs/ai_lead_intake_bitrix24_tz_v1_0.md`

## Task
Audit the existing skeleton, settings layer, and healthcheck endpoint.
Only fix concrete gaps, regressions, or missing tests/docs.

## Files to create/change
- `app/main.py`
- `app/config.py`
- `app/api/health.py`
- related tests
- minimal supporting files only if a verified gap requires them

## Implementation constraints
- Do not recreate the skeleton from scratch.
- Preserve the existing application factory shape unless a concrete bug requires change.
- Do not expand into intake, AI, Bitrix24, routing, worker, or dashboard work.

## Non-goals
- No new architecture.
- No feature expansion outside skeleton/config/health.

## Acceptance criteria
- Existing skeleton behavior is verified or corrected.
- `/health` returns a healthy response.
- Config values load from environment cleanly.
- No already-implemented later-epic behavior is rewritten under this epic.

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
- EPIC 10 — Portfolio Packaging, or another epic only if a verified gap is found
