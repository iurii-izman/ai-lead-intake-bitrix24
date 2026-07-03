# Cursor Prompt — EPIC 04 AI Classifier

## Critical instruction

Do not modify Bitrix24 adapter.
Do not implement routing engine.
Do not implement worker pipeline.
Do not call Bitrix24.

This epic only implements AI provider abstraction and classification persistence.

AI_PROVIDER=mock must work without API keys.
AI_PROVIDER=openai must be isolated behind provider/client boundary.

## Source of truth

`docs/ai_lead_intake_bitrix24_tz_v1_0.md`

## Acceptance criteria

- mock classifier works;
- OpenAI provider boundary exists;
- invalid output → review classification result;
- low confidence → review classification result;
- no real network calls in tests.
