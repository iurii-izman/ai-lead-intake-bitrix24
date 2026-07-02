# ADR 004 — AI Structured Outputs

## Status
Accepted

## Context
AI output must be machine-readable, validated, and safe for routing decisions.

## Decision
- `AI_PROVIDER=mock|openai`.
- Use a provider abstraction.
- Use Structured Outputs / JSON Schema.
- Validate with Pydantic.
- Invalid output or low confidence goes to `review_needed`.

## Consequences
- AI errors do not leak into the rest of the pipeline.
- Mock and real modes share the same contract.

## Alternatives considered
- Free-form text parsing.
- Unvalidated model responses.
