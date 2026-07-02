# Cursor Prompt — EPIC 05 Routing Engine

## Context
The classifier is available; now convert its output into deterministic routing decisions.
Check current files before editing and keep the scope limited to routing rules and decisions.

## Source of truth
`docs/ai_lead_intake_bitrix24_tz_v1_0.md`

## Task
Implement rule-based routing with clear fallback behavior.

## Files to create/change
- `app/services/routing_engine.py` or equivalent
- Routing configuration file(s)
- Tests for matching, fallback, drop, and review paths

## Implementation constraints
- Keep rule evaluation deterministic and readable.
- Prefer declarative routing config over hardcoded branching.
- Do not introduce Bitrix API calls or dashboard changes.
- If a rule shape would require a new architecture decision, stop and record it in an ADR.

## Non-goals
- No Bitrix API work.
- No dashboard polish.

## Acceptance criteria
- Same input yields the same decision.
- Review and drop paths are explicit.
- Fallback behavior is covered by tests.

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
- EPIC 06 — Bitrix24 Adapter
