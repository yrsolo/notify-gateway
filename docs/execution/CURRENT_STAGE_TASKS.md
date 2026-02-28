# Current stage tasks

Текущая стадия: **Stage 1 — Repo hardening (foundation)**.

> Формат задачи: ID / описание / критерий приёмки / артефакт / статус.

## Backlog Stage 1

- [ ] **S1-T01** Создать каркас инфраструктурных каталогов.
  - Приёмка: в репозитории присутствуют `infra/env`, `infra/function/env`, `infra/scripts`, `.github/workflows`.
  - Артефакт: структура директорий в git.

- [ ] **S1-T02** Добавить шаблоны env-конфигов.
  - Приёмка: есть `infra/env/dev.env.example`, `infra/env/prod.env.example`, `infra/function/env/common.env.example`, `infra/function/env/prod.env.example`.
  - Артефакт: коммит с файлами-шаблонами без секретов.

- [ ] **S1-T03** Добавить CI workflow для pull request.
  - Приёмка: `.github/workflows/ci.yml` запускает lint + `pytest -q`.
  - Артефакт: зелёный прогон CI на PR.

- [ ] **S1-T04** Зафиксировать security guardrails для CI.
  - Приёмка: документировано, что секреты не пишутся в лог; запрещён `set -x` в секретных шагах.
  - Артефакт: обновление документации + (опц.) проверочный скрипт.

- [ ] **S1-T05** Обновить runbook локального запуска.
  - Приёмка: README/docs описывает, как локально запускать тесты и что требуется из env.
  - Артефакт: обновлённый раздел в `README.md`/`docs`.

## WIP limit
- Одновременно в `in_progress` не более 2 задач.

## Definition of Done for Stage 1
- [ ] S1-T01 завершена
- [ ] S1-T02 завершена
- [ ] S1-T03 завершена
- [ ] S1-T04 завершена
- [ ] S1-T05 завершена
