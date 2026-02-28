# Текущий статус интеграции с Yandex Cloud (Cloud Codex)

Обновлено: текущая итерация.

## Что уже подтверждено

- `YC_TOKEN` доступен в runtime.
- Доступ к YC API работает из текущего окружения.
- Через API получены:
  - cloud: `b1g6d49mf4scmtn4kjki` (`cloud-yrsolo`),
  - folders: `b1grb7g3424n7dgl5qli` (`datalens`) и `b1g42qj26s1u7gv7bufm` (`read`).
- В репозитории есть fallback-скрипт API-discovery для случаев без `yc` CLI.

## Текущий фокус

Переход к старту цикла разработки:
1. Зафиксировать список обязательных данных/секретов для MVP.
2. Проверить, какие из них получаем из YC API, какие — из Lockbox.
3. Подготовить целевую структуру репозитория для CI/CD и деплоя.
4. Подготовить план GitHub Actions: сбор env/secrets из Lockbox и деплой в Cloud Function + API Gateway.

## Следующие шаги

- На базе `docs/PLAN.md` реализовать итерацию 1 (repo hardening):
  - каркас `infra/env`, `infra/function/env`, `infra/scripts`,
  - `ci.yml` для тестов.
- Далее итерация 2:
  - `deploy.yml` для `main`,
  - скрипты `yc_collect_context.sh` и `yc_deploy_function.sh`,
  - smoke-check после деплоя.
