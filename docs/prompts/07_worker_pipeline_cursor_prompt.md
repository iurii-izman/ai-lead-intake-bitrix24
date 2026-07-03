# Cursor Prompt — EPIC 07 Worker Pipeline

## Critical instruction

Use existing service boundaries.

Do not rewrite:
- AI classifier;
- routing engine;
- Bitrix24 adapter.

The worker should orchestrate existing services:
intake request → AI classification → confidence gate → routing → Bitrix sync → completed/review/dropped/failed.

## Source of truth

`docs/ai_lead_intake_bitrix24_tz_v1_0.md`

## Acceptance criteria

- processes `received` and `failed_retryable`;
- respects retry count;
- low confidence → review;
- spam/drop → dropped;
- temporary Bitrix errors → failed_retryable;
- retry exceeded → failed;
- logs every step.
