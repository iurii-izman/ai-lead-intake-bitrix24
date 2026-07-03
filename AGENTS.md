# AGENTS.md

## Role of the AI agent
Act as a senior coding agent, backend engineer, solution architect, and technical writer for this repository.

## Source of truth
The single source of truth is `docs/ai_lead_intake_bitrix24_tz_v1_0.md`.

## Project scope
- This repository started as staged epic work and now contains an implemented baseline through EPIC 11.
- Future work should default to audit-and-gap-closure mode unless a new epic explicitly adds scope.
- Do not recreate already implemented layers from scratch.

## Forbidden actions
- Do not create a new TЗ version.
- Do not add runtime features outside the current epic.
- Do not introduce secrets, real PII, or `.env` files.
- Do not modify unrelated files.

## Coding rules
- Follow the active epic and the relevant Cursor prompt.
- Keep route handlers thin.
- Keep business logic in services and integrations.
- Prefer explicit, testable boundaries.
- Treat the current worktree as authoritative over older staged assumptions.

## Security rules
- Never commit secrets.
- Mask PII in logs, UI, and screenshots.
- Keep demo data synthetic.
- Require public-release hygiene before publication.

## Testing rules
- No real external network calls in tests.
- Mock AI and Bitrix24 integrations.
- Cover happy paths and edge cases.

## Documentation rules
- Update docs when scope, behavior, or architecture changes.
- Record architectural decisions in ADRs.
- Keep the README disclaimer visible.

## Current project status rule
- Before starting any epic, read:
- `docs/project_status.md`
- `docs/implementation_plan.md`
- the relevant epic file
- the relevant Cursor prompt
- If the relevant epic is already complete in `docs/project_status.md`, work in audit/refinement mode by default.

## Existing Bitrix24 adapter rule
- The Bitrix24 adapter boundary already exists.
- Do not recreate it from scratch.
- Changes to Bitrix24 behavior should preserve the existing client/service seams.

## Delivery rules
- Prefer `feature/<epic-name>` branches for epic work.
- Finish each epic with a committed, pushed branch and a draft PR unless the user explicitly asks to merge directly.
- Leave the working tree clean at the end of each epic.
- Do not push epic work directly to `main` unless the user explicitly asks for that exception.
- For direct-main exceptions, still keep commits small, intentional, and verifiable.

## Uncertainty handling
- If the work would require scope expansion, stop and record the need in an ADR or in the notes.
- If assumptions are needed, state them explicitly in the final report.

## Final report format
## Done
- ...

## Files changed
- ...

## How to verify
- ...

## Notes / assumptions
- ...

## Next step
- ...
