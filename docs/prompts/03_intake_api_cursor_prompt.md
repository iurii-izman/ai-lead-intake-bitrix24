# Cursor Prompt — EPIC 03 Intake API + Security + Idempotency

## Critical instruction

Do not recreate the intake endpoint from scratch.

This epic is already implemented in the repository baseline.

Use this prompt only to audit or refine:
- `POST /api/v1/intake`;
- webhook-secret protection;
- idempotency behavior;
- intake logging;
- intake rate limiting;
- intake-focused tests and docs.

Do not mix in AI, Bitrix24 sync, routing, or worker orchestration changes unless a verified bug crosses the boundary.

## Source of truth

`docs/ai_lead_intake_bitrix24_tz_v1_0.md`

## Acceptance criteria

- valid request → 202;
- duplicate idempotency key → existing request returned;
- invalid secret → 401;
- invalid payload → 422;
- processing log `intake_received` created.
- rate limit rejects excess requests with `429`.
