# Cursor Prompt — EPIC 04 AI Classifier

## Context
Create a provider-based classifier that returns validated structured output.

## Source of truth
`docs/ai_lead_intake_bitrix24_tz_v1_0.md`

## Task
Implement mock and real AI provider modes with strict output validation.

## Files to create/change
- Classifier service
- AI provider client
- Structured output schemas

## Non-goals
- No routing engine implementation.
- No CRM writes.

## Acceptance criteria
- Mock mode is deterministic.
- Real mode returns Pydantic-validated output.
- Invalid output falls back to review.

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
- EPIC 05 — Routing Engine
