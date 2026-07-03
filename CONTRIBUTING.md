# Contributing

## Project posture

This repository is a demo/product prototype with production-capable seams.

Before changing anything:
- read `docs/project_status.md`
- read `docs/implementation_plan.md`
- read the relevant epic doc
- read the relevant prompt if the work is epic-shaped

## Working style

- Prefer small, auditable changes.
- Keep route handlers thin.
- Keep business logic in services and integrations.
- Do not recreate implemented layers from scratch.
- For EPIC 02 and later, use audit-and-gap-closure mode unless the docs explicitly say otherwise.

## Safety rules

- Never commit secrets.
- Never commit real PII.
- Keep demo data synthetic.
- Preserve masking in UI, docs, and screenshots.

## Verification

Run before proposing merge:

```bash
pytest -q
ruff check .
```

If the work affects demo flow or packaging, also verify the relevant walkthrough or seed path.

## Pull requests

- Keep scope aligned with one epic or one concrete maintenance task.
- Update docs when behavior, scope, or repo posture changes.
- Use the PR template.
