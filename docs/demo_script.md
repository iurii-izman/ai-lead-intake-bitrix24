# Demo Script

Source of truth: `docs/ai_lead_intake_bitrix24_tz_v1_0.md`

## Purpose

This is the short talk track for a live portfolio walkthrough.

Target length:
- short version: 3-4 minutes
- standard version: 5-7 minutes

## Opening

AI Lead Intake for Bitrix24 is a demo-first but production-capable CRM intake automation prototype.

It accepts incoming requests, stores them idempotently, classifies them through an AI boundary, routes them deterministically, creates CRM and task entities in Bitrix24, and sends uncertain cases to human review.

## Section 1: Why this exists

The business problem is typical CRM intake chaos:
- requests arrive from multiple channels;
- managers sort them manually;
- duplicates and delays appear;
- routing is inconsistent;
- first response quality varies.

This project inserts a controlled automation layer between intake and Bitrix24.

## Section 2: Architecture

What I usually show:
- the intake API;
- a DB-backed queue;
- an in-process worker;
- an AI classifier;
- a routing engine;
- a Bitrix24 adapter;
- an admin review surface;
- timeline logging.

Key point:
- the first delivery is a demo/product prototype, but the boundaries are designed so the system can evolve without rewriting the whole core.

## Section 3: Live flow

What I say while showing the app:

1. I submit a request through `POST /api/v1/intake`.
2. The API validates it, enforces a webhook secret and idempotency, and stores it quickly.
3. The worker processes it asynchronously.
4. AI returns a structured classification.
5. Routing decides whether it should be reviewed, dropped, or synced.
6. In mock mode the Bitrix adapter creates synthetic CRM and task entities.
7. The admin UI shows the full masked timeline.

## Section 4: Human review principle

This is not “AI decides everything”.

If confidence is low or the payload is ambiguous, the request goes to manual review.

That keeps the system credible for business-process automation instead of turning it into an unsafe black box.

## Section 5: Engineering strengths

What I emphasize:
- explicit state machine;
- idempotency;
- retry semantics;
- isolated integration boundaries;
- public-safe masking;
- mock and real modes;
- test coverage without real external calls.

## Section 6: Honest positioning

This is not positioned as a live commercial deployment.

It is a portfolio-quality demo/product prototype with production-capable seams.

That is important because it keeps the claims honest while still showing real engineering judgment.

## Short closing

The main value of the project is not just “AI parsing text”.

It is the combination of:
- CRM automation thinking;
- integration boundaries;
- operational visibility;
- safe human-in-the-loop behavior;
- and delivery discipline around a realistic end-to-end workflow.
