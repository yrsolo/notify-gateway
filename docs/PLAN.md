# notify-gateway — план и факт выполнения

> Документ синхронизирован с фактической реализацией в репозитории.

## 1) MVP scope

- `POST /notify`
- Bearer-авторизация по API key
- валидация payload
- пересылка в Telegram Bot API
- деплой в Yandex Cloud Functions + API Gateway
- хранение секретов вне git (GitHub Secrets/Lockbox)

## 2) Статус roadmap

### Stage 0 — Discovery + readiness
- [x] Подтверждены cloud/folder контексты и базовый доступ к YC API.
- [x] Зафиксированы источники данных: YC API / Lockbox / repo config.

### Stage 1 — Repo hardening
- [x] Подготовлена структура `infra/` и `*.env.example`.
- [x] Добавлен `ci.yml` (lint + tests).

### Stage 2 — Deploy automation
- [x] Добавлены скрипты deploy-контура (`yc_collect_context.sh`, `yc_deploy_function.sh`, `yc_apply_apigw.sh`).
- [x] Добавлен `deploy.yml` (`push main` + `workflow_dispatch`).
- [x] Добавлен bootstrap endpoint/gateway (`yc_bootstrap_notify_endpoint.sh`).

### Stage 3 — Runtime validation
- [x] Реализован smoke-check (`infra/scripts/smoke_notify.sh`).
- [x] Smoke-check встроен в deploy workflow.
- [x] Документирован rollback runbook и observability/SLO-lite.

### Stage 4 — Production readiness
- [x] Описан регламент ротации секретов.
- [x] Зафиксирована IAM least-privilege матрица.
- [x] Добавлен on-call/ops playbook.
- [x] Выполнены maintenance-улучшения deploy-контура (alias переменных, убран `rg` dependency, поддержка `NOTIFY_PUBLIC_BASE_URL`).

## 3) Текущее состояние

Основной roadmap закрыт. Проект в режиме сопровождения: вносятся точечные изменения в automation и документацию.
