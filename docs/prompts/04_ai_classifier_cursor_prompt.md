# Cursor Prompt — EPIC 04 AI Classifier

## Context
Create a provider-based classifier that returns validated structured output.
Inspect the current repository state and do not modify unrelated modules.

## Source of truth
`docs/ai_lead_intake_bitrix24_tz_v1_0.md`

## Task
Implement mock and real AI provider modes with strict output validation.

## Files to create/change
- `app/services/ai_classifier.py` or equivalent service
- `app/integrations/llm_client.py` or equivalent provider client
- Structured output schemas and validation models
- Tests for mock, invalid, and low-confidence responses

## Implementation constraints
- The output contract must be Pydantic-validated.
- The mock provider must be deterministic.
- Invalid JSON or validation errors must route to review.
- Do not add routing, Bitrix, or dashboard logic here.

## Non-goals
- No routing engine implementation.
- No CRM writes.

## Acceptance criteria
- Mock mode is deterministic.
- Real mode returns Pydantic-validated output.
- Invalid output falls back to review.
- The implementation remains provider-agnostic.

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
