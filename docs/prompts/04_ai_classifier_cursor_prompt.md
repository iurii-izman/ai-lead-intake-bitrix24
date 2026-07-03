# Cursor Prompt — EPIC 04 AI Classifier

## Critical instruction

Do not recreate the classifier or provider boundary from scratch.

This epic is already implemented in the repository baseline.

Use this epic to audit and improve:
- provider abstraction;
- mock/OpenAI mode behavior;
- structured-output validation;
- fallback and review-gate handling;
- AI-related tests and docs.

Keep Bitrix24, routing, and worker changes out unless a verified boundary bug requires a minimal coordinated fix.

## Source of truth

`docs/ai_lead_intake_bitrix24_tz_v1_0.md`

## Acceptance criteria

- mock classifier works;
- OpenAI provider boundary exists;
- invalid output → review classification result;
- low confidence → review classification result;
- no real network calls in tests.
