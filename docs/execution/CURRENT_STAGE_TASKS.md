# Current stage tasks

Текущая стадия: **Stage 1 — Repo hardening (foundation)**.

> Формат: ID / описание / owner / оценка / критерии приёмки / артефакт проверки / статус.

## Stage 1 backlog (атомарные задачи)

- [x] **S1-T01** Создать каркас инфраструктурных каталогов.
  - Owner: agent
  - Оценка: 0.25d
  - Критерии приёмки:
    1. В репозитории присутствуют `infra/env`, `infra/function/env`, `infra/scripts`, `.github/workflows`.
  - Артефакт проверки: вывод `find infra .github -maxdepth 3 -type d | sort`.
  - Статус: `done`

- [x] **S1-T02** Добавить шаблоны env-конфигов.
  - Owner: agent
  - Оценка: 0.25d
  - Критерии приёмки:
    1. Есть `infra/env/dev.env.example`.
    2. Есть `infra/env/prod.env.example`.
    3. Есть `infra/function/env/common.env.example`.
    4. Есть `infra/function/env/prod.env.example`.
    5. В шаблонах нет реальных секретов.
  - Артефакт проверки: содержимое `*.env.example` + `git status` без новых `.env`.
  - Статус: `done`

- [x] **S1-T03** Добавить CI workflow для pull request.
  - Owner: agent
  - Оценка: 0.5d
  - Критерии приёмки:
    1. `.github/workflows/ci.yml` запускается на `pull_request`.
    2. Workflow выполняет lint (`ruff check .`) и тесты (`pytest -q`).
  - Артефакт проверки: файл `.github/workflows/ci.yml`.
  - Статус: `done`

- [x] **S1-T04** Зафиксировать security guardrails для CI.
  - Owner: agent
  - Оценка: 0.25d
  - Критерии приёмки:
    1. Документировано, что секреты не пишутся в лог.
    2. Для секретных шагов запрещён `set -x`.
    3. Для infra-скриптов зафиксировано `set -euo pipefail`.
  - Артефакт проверки: `docs/security/CI_GUARDRAILS.md`.
  - Статус: `done`

- [x] **S1-T05** Обновить runbook локального запуска.
  - Owner: agent
  - Оценка: 0.25d
  - Критерии приёмки:
    1. README описывает локальный запуск проверок.
    2. README ссылается на env-шаблоны и CI workflow.
  - Артефакт проверки: обновлённый `README.md`.
  - Статус: `done`

## WIP limit
- Одновременно в `in_progress` не более 2 задач.
- Фактически в работе одновременно: 1 задача (последовательное выполнение).

## Definition of Done for Stage 1
- [x] S1-T01 завершена
- [x] S1-T02 завершена
- [x] S1-T03 завершена
- [x] S1-T04 завершена
- [x] S1-T05 завершена
