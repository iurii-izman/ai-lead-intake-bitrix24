# EPIC 06 — Bitrix24 Adapter

## Goal
Synchronize approved routing outcomes into Bitrix24 with isolated integration logic.

## Source of truth
`docs/ai_lead_intake_bitrix24_tz_v1_0.md`

## Scope
- Mock and real Bitrix modes.
- Universal and legacy CRM modes.
- Task creation.

## Out of scope
- OAuth marketplace app.
- SaaS multi-tenant work.

## Expected files
- Bitrix client
- Sync service
- Field mapping config

## Implementation notes
- Keep the adapter boundary strict.
- Encode portal differences outside the business logic.
- Any new integration shape must be justified by ADR.

## Acceptance criteria
- CRM and task sync paths are isolated and testable.

## Definition of Done
- Bitrix integration can be mocked or run against a real portal safely.

## Cursor prompt location
`docs/prompts/06_bitrix24_adapter_cursor_prompt.md`
