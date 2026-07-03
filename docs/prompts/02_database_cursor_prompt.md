# Cursor Prompt — EPIC 02 Database + State Machine

## Critical instruction

Do not recreate the persistence layer from scratch.

This epic is already implemented in the repository baseline.

Use this prompt only to:
- audit database models and schema boundaries;
- verify state enum and transition logic;
- close concrete gaps in models, state machine, or DB tests;
- align docs if the persistence contract changes.

Do not use this epic to rewrite intake, AI, routing, Bitrix24, worker, or dashboard logic.

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

- table creation still works;
- state transitions remain explicit and testable;
- persistence changes stay backward-compatible with the current codebase unless an ADR says otherwise;
- no external network calls;
- relevant tests pass.
