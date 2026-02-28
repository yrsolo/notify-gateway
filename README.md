# notify-gateway

Сервис-шлюз для централизованной отправки уведомлений из разных проектов в Telegram через единый HTTP endpoint.

## Текущий статус

Сейчас репозиторий находится на **этапе планирования**: зафиксированы границы MVP, план работ и требования к окружению/доступам.

- План этапов: `docs/PLAN.md`
- Переменные окружения и доступы для Yandex Cloud: `docs/ENV_AND_ACCESS.md`
- Текущий операционный статус и блокеры Codex/YC: `docs/STATUS.md`

## Цель MVP

- `POST /notify`
- Bearer-авторизация по API key
- валидация payload
- пересылка в Telegram Bot API
- деплой в Yandex Cloud Functions + API Gateway
- секреты только в env/secret storage

## Что будет в следующем этапе

1. Реализация `src/handler.py` под Python 3.11.
2. Минимальные тесты (`401/400/200`).
3. Базовый `infra/apigw.yaml`.
4. Короткая инструкция деплоя.
