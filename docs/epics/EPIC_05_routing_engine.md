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

## Cursor prompt location
`docs/prompts/05_routing_engine_cursor_prompt.md`
