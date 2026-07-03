# GitHub Workflow

Source of truth: `docs/ai_lead_intake_bitrix24_tz_v1_0.md`

## Repo posture
- Private-first repository until the public-safe checklist is complete.
- Demo data must remain synthetic.
- No secrets, real PII, or production credentials in the repo.

## Branch strategy
- `main` for stable merged work.
- `dev` for integration work when needed.
- `feature/<epic-name>` for a single epic at a time.
- Epic work should land through a feature branch and draft PR, not directly into `main`.

## Commit convention
- `docs:`
- `chore:`
- `feat:`
- `fix:`
- `test:`
- `security:`
- `refactor:`

## Pull request flow
- One epic per branch.
- Review scope before merge.
- Run tests before merge.
- Check docs and checklists before merge.
- Finish with a clean working tree before handing off.

## Quality gates
- Scope stays within the current epic.
- No unrelated files are changed without reason.
- No secrets, `.env`, DB dumps, or logs are committed.
- Public-release checklist is completed before publication.

## Public release notes
- Confirm screenshots are masked.
- Confirm README disclaimer is present.
- Confirm demo data is synthetic.
- Use [docs/release_note.md](./release_note.md) as the canonical public-safe release text.
