# Current stage tasks

Текущая стадия: **Stage 4 — Production readiness (maintenance mode)**.

> Формат: ID / описание / owner / оценка / критерии приёмки / артефакт проверки / статус.

## Stage 4 backlog (атомарные задачи)

- [x] **S4-T01** Описать регламент ротации секретов и расписание.
  - Owner: agent
  - Оценка: 0.5d
  - Критерии приёмки:
    1. Документированы scope, периодичность и шаги ротации.
    2. Есть checklist верификации после ротации.
  - Артефакт проверки: `docs/SECRET_ROTATION.md`.
  - Статус: `done`

- [x] **S4-T02** Провести ревизию IAM ролей и предложить least-privilege матрицу.
  - Owner: agent
  - Оценка: 0.5d
  - Критерии приёмки:
    1. Зафиксирован текущий набор ролей.
    2. Сформирована целевая минимальная матрица ролей.
  - Артефакт проверки: `docs/IAM_LEAST_PRIVILEGE.md`.
  - Статус: `done`

- [x] **S4-T03** Обновить on-call/ops документацию и runbook инцидентов.
  - Owner: agent
  - Оценка: 0.5d
  - Критерии приёмки:
    1. Описаны каналы эскалации и SLA реакции.
    2. Есть playbook по типовым инцидентам.
  - Артефакт проверки: `docs/ONCALL_OPS_PLAYBOOK.md`.
  - Статус: `done`

- [x] **S4-T04** Добавить совместимость с alias `YC_CLOUD_FUNCTION_NAME` для deploy workflow.
  - Owner: agent
  - Оценка: 0.25d
  - Критерии приёмки:
    1. Workflow принимает `YC_FUNCTION_NAME` или alias `YC_CLOUD_FUNCTION_NAME`.
    2. Ошибка валидации подсказывает корректные имена переменных.
  - Артефакт проверки: `.github/workflows/deploy.yml`.
  - Статус: `done`

- [x] **S4-T05** Добавить bootstrap-скрипт для восстановления `YC_API_GW_NAME` и `NOTIFY_ENDPOINT`.
  - Owner: agent
  - Оценка: 0.5d
  - Критерии приёмки:
    1. Скрипт создаёт/обновляет gateway и печатает значения endpoint.
    2. Поддержана опциональная синхронизация значений в Lockbox.
  - Артефакт проверки: `infra/scripts/yc_bootstrap_notify_endpoint.sh`, `docs/DEPLOY_RUNBOOK.md`.
  - Статус: `done`

- [x] **S4-T06** Убрать hard-dependency от `rg` в bootstrap API Gateway.
  - Owner: agent
  - Оценка: 0.25d
  - Критерии приёмки:
    1. Скрипт bootstrap не требует установленный `rg` на GitHub runner.
    2. Проверка плейсхолдеров выполняется стандартным POSIX/Ubuntu инструментом.
  - Артефакт проверки: `infra/scripts/yc_bootstrap_notify_endpoint.sh`.
  - Статус: `done`

- [x] **S4-T07** Поддержать публичный домен API в bootstrap/deploy.
  - Owner: agent
  - Оценка: 0.25d
  - Критерии приёмки:
    1. Bootstrap-скрипт поддерживает override endpoint через переменную окружения.
    2. Deploy workflow прокидывает переменную публичного base URL.
    3. Runbook описывает настройку домена и переменных.
  - Артефакт проверки: `infra/scripts/yc_bootstrap_notify_endpoint.sh`, `.github/workflows/deploy.yml`, `docs/DEPLOY_RUNBOOK.md`.
  - Статус: `done`

## Program status
- Все стадии `Stage 0..4` закрыты по execution-трекеру.
- Репозиторий находится в maintenance mode: только change-requests и актуализация runbook.

## WIP limit
- Одновременно в `in_progress` не более 2 задач.
- Текущее состояние: 0 `in_progress`.
