# Notion Case Structure

Source of truth: `docs/ai_lead_intake_bitrix24_tz_v1_0.md`

## Purpose
This page is a public-safe portfolio case for GitHub, Notion, or a recruiter-facing share link.

## Public-safe disclaimer
Demo case / product prototype. This is not a commercial deployment.
The architecture is production-capable; the first delivery is a portfolio/demo MVP.

## Suggested page outline
1. Title
2. Disclaimer
3. Problem statement
4. Solution summary
5. Architecture
6. Data flow
7. AI classification
8. Routing engine
9. Bitrix24 integration
10. Human-in-the-loop review
11. Production-thinking elements
12. Demo vs production scope
13. Screenshots
14. Trade-offs and exclusions
15. Repository link

## Copy block for the title section
AI Lead Intake for Bitrix24

## Copy block for the summary
AI Lead Intake for Bitrix24 is a production-capable demo/product prototype that accepts incoming requests, classifies them with AI, routes them according to deterministic rules, creates CRM records and tasks in Bitrix24, keeps a draft reply, and sends uncertain cases to human review.

## What to emphasize publicly
- Synthetic data only
- PII masking in logs and UI
- Mock and real integration seams
- Idempotency and retry handling
- Human review for low-confidence cases
- Clear demo-first positioning

## What to avoid publicly
- Claims of a live commercial deployment
- Real customer data
- Secrets, webhooks, and environment values
- Unmasked screenshots
- Internal-only implementation notes

## Visuals to attach
- Architecture diagram
- Dashboard queue
- Request detail page
- AI classification result
- Bitrix24 sync result

## Footer note
If a reader wants the technical background, point them to `README.md`, `docs/architecture.md`, and the source repository.
