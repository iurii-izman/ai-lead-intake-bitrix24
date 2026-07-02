# EPIC 04 — AI Classifier

## Goal
Classify incoming requests into structured outputs suitable for routing.

## Source of truth
`docs/ai_lead_intake_bitrix24_tz_v1_0.md`

## Scope
- Provider abstraction.
- Mock and real AI modes.
- Structured output validation.

## Out of scope
- CRM sync.
- Dashboard actions.

## Expected files
- Classifier service
- AI provider client
- Output schemas

## Implementation notes
- Invalid output should fail into review.
- Use Pydantic validation on the response.
- No hidden manual branching in route handlers.
- Any provider or schema expansion outside this epic needs an ADR before implementation.

## Acceptance criteria
- Mock mode is deterministic.
- Real mode returns validated structured data.

## Definition of Done
- AI output is stable, validated, and review-aware.
- Mock and real provider behavior share the same contract.

## Cursor prompt location
`docs/prompts/04_ai_classifier_cursor_prompt.md`
