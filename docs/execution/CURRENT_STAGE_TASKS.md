# Current stage tasks

Текущая стадия: **Stage 3 — Runtime validation & observability**.

> Формат: ID / описание / owner / оценка / критерии приёмки / артефакт проверки / статус.

## Stage 2 completion snapshot

- [x] S2-T01 `yc_collect_context.sh`
- [x] S2-T02 `yc_deploy_function.sh`
- [x] S2-T03 `.github/workflows/deploy.yml`
- [x] S2-T04 API Gateway apply/validate step (`yc_apply_apigw.sh` + workflow)
- [x] S2-T05 Deploy runbook + rollback docs

Stage 2 DoD: **выполнен**.

## Stage 3 backlog (атомарные задачи)

- [ ] **S3-T01** Добавить smoke-check скрипт для `POST /notify`.
  - Owner: agent
  - Оценка: 0.5d
  - Критерии приёмки:
    1. Есть скрипт `infra/scripts/smoke_notify.sh` с `set -euo pipefail`.
    2. Скрипт валидирует HTTP-код и формат JSON ответа.
    3. Поддержан безопасный dry-run/skip-send режим.
  - Артефакт проверки: `bash -n infra/scripts/smoke_notify.sh` + dry-run вывод.
  - Статус: `todo`

- [ ] **S3-T02** Встроить smoke-check в deploy pipeline.
  - Owner: agent
  - Оценка: 0.5d
  - Критерии приёмки:
    1. После деплоя запускается smoke-check.
    2. Падение smoke-check фейлит workflow.
  - Артефакт проверки: `.github/workflows/deploy.yml`.
  - Статус: `todo`

- [ ] **S3-T03** Документировать rollback-runbook с операционными шагами.
  - Owner: agent
  - Оценка: 0.5d
  - Критерии приёмки:
    1. Описан rollback функции и gateway.
    2. Описаны проверки после rollback.
  - Артефакт проверки: `docs/DEPLOY_RUNBOOK.md`.
  - Статус: `todo`

- [ ] **S3-T04** Зафиксировать SLO-lite и operational checks.
  - Owner: agent
  - Оценка: 0.5d
  - Критерии приёмки:
    1. Описаны критерии успешности (например, доля 2xx smoke-check).
    2. Описаны источники логов и триггеры эскалации.
  - Артефакт проверки: новый документ в `docs/`.
  - Статус: `todo`

## WIP limit
- Одновременно в `in_progress` не более 2 задач.
- Текущее состояние: 0 `in_progress`.

## Definition of Done for Stage 3
- [ ] S3-T01 завершена
- [ ] S3-T02 завершена
- [ ] S3-T03 завершена
- [ ] S3-T04 завершена
