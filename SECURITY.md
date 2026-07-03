# Security Policy

## Repository scope

This repository is a public-safe demo/product prototype.

It must not contain:
- secrets
- production credentials
- real customer data
- unmasked screenshots with personal data

## Expected safeguards

- `.env` is ignored
- demo data is synthetic
- intake payloads are masked for storage and presentation
- admin UI is protected with Basic Auth
- intake API is protected with `X-Webhook-Secret`
- tests do not use real external network calls

## Reporting

If you find a security issue in the repository:
- do not publish secrets or sensitive payloads in a public issue
- redact all PII and credentials
- provide reproduction steps with synthetic data when possible

## Notes

This repository is not positioned as a live commercial deployment. Security hardening for an internal-production rollout would require stronger auth, secret management, audit controls, and deployment posture than the current portfolio baseline.
