# Cursor Prompt — EPIC 05 Routing Engine

## Critical instruction

Do not recreate routing from scratch.

This epic is already implemented in the repository baseline.

Use this epic to audit and refine deterministic routing decisions, rule loading, fallback paths, and routing tests.

Do not expand into Bitrix24 sync or worker orchestration except for a minimal boundary fix backed by failing tests or a verified bug.

## Source of truth

`docs/ai_lead_intake_bitrix24_tz_v1_0.md`

## Acceptance criteria

- reads `config/routing.yaml`;
- top-down rules;
- fallback;
- spam/drop action;
- safe template formatting;
- no eval;
- tests for rules.
