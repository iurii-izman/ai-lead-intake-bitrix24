# ADR 006 — Demo vs Production

## Status
Accepted

## Context
The project must look credible as engineering work while staying achievable for a first delivery.

## Decision
- Production-capable architecture.
- Demo-first delivery.
- Avoid enterprise overengineering in the MVP.
- Keep a roadmap to an internal production app.

## Consequences
- The project can be delivered quickly without painting itself into a corner.
- Later production hardening should require extension, not a rewrite.

## Alternatives considered
- Build everything as full enterprise production from day one.
- Build a throwaway demo with no upgrade path.
