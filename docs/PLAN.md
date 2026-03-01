# Notify Gateway — Roadmap

This repository contains a small HTTP gateway for sending notifications to Telegram via Yandex Cloud Functions + API Gateway.

## Principles
- Keep runtime simple (single handler, minimal deps).
- Grow by small PRs (1–3 hours each).
- Strong contracts: validation, stable error format, safe logging.
- CI must stay reliable; deploy must be reproducible.

## Stages and priorities

### Stage S4 — Stabilize CI/Deploy (P0)
Goal: remove dependency on `yc` CLI from GitHub Actions and make deploy/bootstrap less fragile.

Tasks (P0):
- S4-T08A: Replace yc CLI bootstrap with Python-based YC API client
- S4-T08B: Update GitHub Actions workflow to use the new bootstrap tool
- S4-T08C: Add smoke-tests for bootstrap + endpoint
- S4-T08D: Document new CI secrets/env and rollback procedure

### Stage S5 — Product features (P1)
Goal: add small product improvements without turning handler into a monolith.

Tasks (P1):
- S5-T09: Message templates (notification / error / raw)
- S5-T10: Chat routing (chat_id override + aliases)
- S5-T11: Help mode/endpoint (documented usage + examples)

### Stage S6 — Reliability & polish (P2)
Goal: improve reliability and maintainability after P0/P1 are stable.

Tasks (P2):
- S6-T12A: Telegram error mapping + optional retry/backoff
- S6-T12B: Structured logs + request_id correlation
- S6-T12C: Expand contract tests and edge-case coverage
