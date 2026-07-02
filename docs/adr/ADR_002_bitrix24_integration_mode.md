# ADR 002 — Bitrix24 Integration Mode

## Status
Accepted

## Context
Bitrix24 portals differ, and the project must support both demo-safe mock behavior and real portal integration.

## Decision
- `BITRIX_MODE=mock|real`.
- `BITRIX_CRM_MODE=universal|legacy`.
- Primary CRM path: `crm.item.add`.
- Legacy fallback: `crm.lead.add`.
- Task creation: `tasks.task.add`.
- Field mapping lives in `config/field_mapping.yaml`.

## Consequences
- Integration differences stay outside the business logic.
- The same app can demo safely or connect to a real portal.

## Alternatives considered
- Hardcoding a single Bitrix portal shape.
- Embedding field mapping in code.
