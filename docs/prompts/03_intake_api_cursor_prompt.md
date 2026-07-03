# Cursor Prompt — EPIC 03 Intake API + Security + Idempotency

## Critical instruction

Do not call AI.
Do not call Bitrix24.
Do not implement routing.
Do not implement worker pipeline.

This epic only accepts and stores incoming requests.

Existing Bitrix24 adapter must remain untouched.

## Source of truth

`docs/ai_lead_intake_bitrix24_tz_v1_0.md`

## Acceptance criteria

- valid request → 202;
- duplicate idempotency key → existing request returned;
- invalid secret → 401;
- invalid payload → 422;
- processing log `intake_received` created.
