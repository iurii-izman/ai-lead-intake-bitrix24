# Cursor Prompt — EPIC 06 Bitrix24 Adapter Integration Pass

## Critical instruction

Do not recreate the Bitrix24 adapter from scratch.

Before changing anything:
1. Find existing Bitrix24 adapter/service files.
2. Find existing Bitrix24 tests.
3. Find `config/field_mapping.yaml`.
4. Audit what is already implemented.

Expected existing or target capabilities:
- BITRIX_MODE=mock/real.
- BITRIX_CRM_MODE=universal/legacy.
- universal mode uses `crm.item.add` with `entityTypeId=1`.
- legacy mode uses `crm.lead.add`.
- task creation uses `tasks.task.add`.
- field mapping is externalized.
- retry/backoff exists for 429, timeout, 5xx.
- 400 is not retried.
- 401/403 are config/auth failures.
- tests do not make real network calls.

This epic should integrate the adapter with:
- routing decisions;
- `bitrix_entities`;
- processing logs;
- state machine;
- worker pipeline later if EPIC 07 is not yet complete.

If the adapter is already complete, only add missing tests/docs and do not rewrite.

## Source of truth

`docs/ai_lead_intake_bitrix24_tz_v1_0.md`
