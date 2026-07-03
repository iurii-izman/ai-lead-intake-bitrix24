# EPIC 05 — Routing Engine

## Goal
Translate AI output into deterministic routing decisions.

## Source of truth
`docs/ai_lead_intake_bitrix24_tz_v1_0.md`

## Scope
- Rules evaluation.
- Fallback behavior.
- Explicit drop and review paths.

## Out of scope
- Bitrix API calls.
- UI changes.

## Expected files
- Routing service
- Routing config
- Routing tests

## Implementation notes
- Keep rules readable and predictable.
- First matching rule should win unless the ADR says otherwise.
- Do not extend scope without ADR updates.
- Any routing rule model change beyond this epic requires an ADR first.

## Acceptance criteria
- Routing decisions are deterministic and testable.

## Definition of Done
- Requests can be routed, reviewed, or dropped with traceable rules.
- Rule evaluation is deterministic under test.
- Changes are committed, pushed, and handed off via a draft PR unless the user explicitly requests a direct main push.
- Working tree is clean at handoff.

## Actual completion status

Status: complete in the current repository baseline.

Implemented:
- YAML routing config loading;
- top-down deterministic evaluation;
- fallback rule behavior;
- review and drop paths;
- routing tests for critical rules and fallback.

If this epic is revisited, audit and refine the existing routing engine instead of recreating it.

## Cursor prompt location
`docs/prompts/05_routing_engine_cursor_prompt.md`
