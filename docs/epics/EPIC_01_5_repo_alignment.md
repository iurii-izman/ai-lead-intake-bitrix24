# EPIC 01.5 — Repo Alignment & Delivery Baseline

## Goal

Align the repository state, project status, prompts, and public-facing docs with the actual implementation baseline.

## Why this epic exists

The repository moved ahead of the original staged baseline, but status docs and prompts lagged behind the code.

This epic exists to prevent future agents from following outdated greenfield prompts against an already implemented codebase.

## Source of truth

`docs/ai_lead_intake_bitrix24_tz_v1_0.md`

## Scope

- Update README project status.
- Create or update `docs/project_status.md`.
- Update actual completion status across implemented epics.
- Update prompts so they default to audit-and-gap-closure mode instead of recreate-from-scratch mode.
- Reconcile the implementation plan with the real repository baseline.
- Keep guidance explicit about preserving existing Bitrix24, AI, routing, worker, and admin boundaries.

## Out of scope

- No new functional feature work beyond documentation alignment and verified hygiene fixes.
- No new Bitrix24 adapter work.
- No new TЗ version.

## Acceptance criteria

- README reflects the correct current stage.
- `docs/project_status.md` exists and is accurate.
- Implemented epics are marked according to the current repository baseline.
- Prompts prevent accidental rework and scope creep.
- No secrets or real PII are added.
- No unrelated functional application features are introduced.
- Repository guidance is safe for subsequent epic work.

## Definition of Done

- All alignment documents are updated.
- Future Cursor agents can clearly see the current state.
- Subsequent epic work can continue without ambiguity.
- Existing implementation layers are protected from accidental rewrite.

## Actual completion status

Status: complete.

Delivered by this alignment pass:
- repository status synchronized with the actual implemented baseline;
- prompts rewritten toward audit-first execution for implemented epics;
- README and implementation plan reconciled with the current codebase;
- epic files updated with actual completion notes where applicable.
