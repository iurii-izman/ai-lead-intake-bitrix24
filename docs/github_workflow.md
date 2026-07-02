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

## Quality gates
- Scope stays within the current epic.
- No unrelated files are changed without reason.
- No secrets, `.env`, DB dumps, or logs are committed.
- Public-release checklist is completed before publication.

## Public release notes
- Confirm screenshots are masked.
- Confirm README disclaimer is present.
- Confirm demo data is synthetic.
