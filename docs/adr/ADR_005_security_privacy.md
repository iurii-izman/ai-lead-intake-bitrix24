# ADR 005 — Security & Privacy

## Status
Accepted

## Context
The repository must be safe to share publicly and suitable for portfolio review.

## Decision
- No secrets in the repo.
- `.env` is ignored.
- Synthetic demo data only.
- PII masking in logs, UI, and screenshots.
- Basic Auth for admin.
- `X-Webhook-Secret` for intake.
- No real PII in the public repository.

## Consequences
- Public-safe artifact hygiene becomes a first-class requirement.
- Demo assets must be reviewed before publication.

## Alternatives considered
- Relying on manual discipline only.
- Exposing admin UI without auth.
