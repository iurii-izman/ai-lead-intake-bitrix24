# Cursor Prompt — EPIC 05 Routing Engine

## Critical instruction

Do not call Bitrix24.
Do not implement worker pipeline.
Do not modify Bitrix24 adapter.

This epic only converts AI classification into deterministic routing decisions.

## Source of truth

`docs/ai_lead_intake_bitrix24_tz_v1_0.md`

## Acceptance criteria

- reads `config/routing.yaml`;
- top-down rules;
- fallback;
- spam/drop action;
- safe template formatting;
- no eval;
- tests for rules.
