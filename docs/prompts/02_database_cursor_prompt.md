# Cursor Prompt — EPIC 02 Database + State Machine

## Critical instruction

Do not modify Bitrix24 adapter files in this epic.

Do not implement intake API, AI classifier, routing engine, worker, or dashboard.

This epic is only for:
- database models;
- state enum;
- status transitions;
- processing logs;
- Pydantic schemas;
- tests for models and state machine.

Existing early Bitrix24 work must remain untouched.

## Source of truth

`docs/ai_lead_intake_bitrix24_tz_v1_0.md`

## Expected models

- `intake_requests`
- `ai_classifications`
- `routing_decisions`
- `bitrix_entities`
- `processing_logs`

## Statuses

```text
received
processing
classified
review_needed
routed
bitrix_syncing
completed
failed
failed_retryable
dropped
duplicate
```

## Acceptance criteria

- tables can be created;
- state transitions are explicit/testable;
- no external network calls;
- tests pass.
