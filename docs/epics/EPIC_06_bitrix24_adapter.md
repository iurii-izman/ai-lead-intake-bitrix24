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
- If CRM semantics need to change beyond this epic, stop and update the ADR first.

## Acceptance criteria
- CRM and task sync paths are isolated and testable.

## Definition of Done
- Bitrix integration can be mocked or run against a real portal safely.
- CRM and task sync are still isolated from the rest of the codebase.
- Changes are committed, pushed, and handed off via a draft PR unless the user explicitly requests a direct main push.
- Working tree is clean at handoff.

## Actual completion status

Status: complete in the current repository baseline.

Implemented and integrated:
- Mock and real Bitrix24 modes.
- Universal CRM mode via `crm.item.add`.
- Legacy CRM mode via `crm.lead.add`.
- Task creation via `tasks.task.add`.
- Field mapping through `config/field_mapping.yaml`.
- Retry-aware error handling and persistence into `bitrix_entities`.
- Processing logs and worker/admin integration paths.
- Tests without real network calls.

If this epic is revisited, audit and refine the existing adapter instead of recreating it.

## Cursor prompt location
`docs/prompts/06_bitrix24_adapter_cursor_prompt.md`
