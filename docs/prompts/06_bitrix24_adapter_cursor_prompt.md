# Cursor Prompt — EPIC 06 Bitrix24 Adapter

## Context
Implement the integration boundary that syncs approved outcomes into Bitrix24.
Inspect the current repository state first and keep the work inside integration boundaries only.

## Source of truth
`docs/ai_lead_intake_bitrix24_tz_v1_0.md`

## Task
Create mock/real Bitrix modes, CRM mode selection, and task creation.

## Files to create/change
- `app/integrations/bitrix24_client.py` or equivalent client
- `app/services/bitrix_service.py` or equivalent sync service
- `config/field_mapping.yaml` or equivalent mapping file
- Tests for mock mode, real-mode contract, and failure handling

## Implementation constraints
- Support mock and real modes behind one adapter boundary.
- Keep CRM mode selection explicit.
- Use mapping config for portal-specific fields.
- Do not add OAuth, SaaS, or marketplace behavior.

## Non-goals
- No OAuth marketplace app.
- No SaaS work.

## Acceptance criteria
- Adapter isolates integration differences.
- Errors are handled predictably.
- Task creation is part of the same isolated adapter boundary.

## Final report format
## Done
- ...

## Files changed
- ...

## Branch / commit / PR
- Branch:
- Commit:
- Push:
- PR:

## How to verify
- ...

## Notes / assumptions
- ...

## Tree state
- Working tree is clean at the end of the epic.

## Next step
- EPIC 07 — Worker Pipeline
