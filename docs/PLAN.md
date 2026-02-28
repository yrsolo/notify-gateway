# notify-gateway — этап 0: планирование MVP

> Цель этого этапа: ничего не реализуем в коде, только фиксируем план, границы MVP, доступы и порядок работ.

## 1) Цель и границы MVP

### Что делаем в MVP
- Единая точка входа `POST /notify`.
- Авторизация через `Authorization: Bearer <API_KEY>`.
- Валидация входного JSON (обязательные/опциональные поля, типы).
- Отправка сообщения в Telegram Bot API (`sendMessage`).
- Развёртывание в Yandex Cloud Functions + API Gateway.
- Все секреты только в переменных окружения.

### Что НЕ делаем в MVP
- Очереди, ретраи на уровне инфраструктуры, DLQ.
- Дедупликация/антиспам в БД.
- Сложная маршрутизация по нескольким чатам/тредам.
- RBAC-панель, UI, хранение истории уведомлений.

---

## 2) Архитектура MVP (минимальная)

1. Клиентский проект делает `POST /notify` в API Gateway.
2. API Gateway проксирует запрос в Cloud Function.
3. Функция:
   - проверяет Bearer API key;
   - валидирует payload;
   - формирует Telegram message в HTML;
   - вызывает `https://api.telegram.org/bot<TOKEN>/sendMessage`.
4. Функция возвращает JSON-ответ клиенту (`200/400/401/5xx`).

---

## 3) План работ по этапам

## Этап A — Подготовка окружений и доступов (текущий)
- [x] Зафиксировать список env/secret переменных для runtime и deploy.
- [x] Зафиксировать список доступов в Yandex Cloud (Cloud/Folder/SA/roles).
- [ ] Зафиксировать минимальный runbook деплоя.
- [x] Подготовить чеклист готовности перед реализацией.

**Текущий блокер:** runtime сессия Codex не видит `YC_TOKEN`/`YC_FOLDER_ID`, а выход к YC API в текущей сессии отвечает `403 CONNECT tunnel`; до исправления окружения реализацию не начинаем.

## Этап B — Реализация backend MVP
- [ ] Реализовать `src/handler.py` под Python 3.11.
- [ ] Добавить схему валидации и понятные ошибки 400/401.
- [ ] Добавить форматирование Telegram-сообщения с HTML-escape.
- [ ] Добавить unit-тесты (`401`, `400`, `200`, edge-cases).

## Этап C — Infra и публикация
- [ ] Подготовить `infra/apigw.yaml` для `POST /notify`.
- [ ] Описать команды деплоя и обновления функции.
- [ ] Проверить end-to-end через `curl`.

## Этап D — Post-MVP (по желанию)
- [ ] Подпись HMAC вместо/вместе с API key.
- [ ] Idempotency и anti-spam (TTL storage).
- [ ] Маршрутизация по проектам в разные chat/thread.

---

## 4) Критерии готовности MVP

- [ ] `POST /notify` работает через API Gateway.
- [ ] При неверном ключе всегда `401`.
- [ ] При невалидном JSON/типах всегда `400` с понятной ошибкой.
- [ ] При успехе `200` и `telegram_message_id`.
- [ ] В репозитории нет секретов.

---

## 5) Риски и меры

- Риск: неверный `chat_id` или бот не имеет доступа к чату.
  - Мера: smoke-check `getMe`/тестовый `sendMessage` перед запуском.
- Риск: слишком длинные сообщения (`message`, `extra`) и ошибки Telegram.
  - Мера: на этапе реализации добавить лимиты/усечение.
- Риск: ручная ротация API ключей.
  - Мера: хранить ключи только в env/secret manager, ротация по регламенту.

---

## 6) Definition of Ready для старта реализации

Реализацию начинаем только когда:
- [ ] Есть `cloud_id`, `folder_id`.
- [ ] Есть service account(ы) и выданы роли.
- [ ] Есть Telegram bot token и валидный chat_id.
- [ ] Подготовлены runtime/deploy env-переменные (см. `docs/ENV_AND_ACCESS.md`).
- [ ] Согласован API-контракт (поля, ошибки, формат ответа).

---

## 7) Операционный статус preflight (2026-02-28, обновлено)

Проверка повторно выполнена в runtime Codex-сессии.

- `YC_TOKEN`: **не виден** в runtime env (`printenv` пуст по `^YC_`).
- `YC_FOLDER_ID`: **не виден** в runtime env (`printenv` пуст по `^YC_`).
- Сетевой контур:
  - в окружении выставлены `HTTP_PROXY/HTTPS_PROXY=http://proxy:8080`;
  - через прокси `iam.api.cloud.yandex.net` и `api.cloud.yandex.net` отвечают `HTTP 404` на `/` (endpoint достижим);
  - без прокси (`--noproxy '*'`) соединение на `:443` не устанавливается.

### Что это значит

1. Проблема не в коде репозитория: env переменные не проброшены в текущий runtime контейнер.
2. Сеть наружу в этой среде работает через прокси; прямой egress отключён.
3. До появления `YC_TOKEN` в env невозможен авторизованный autodiscovery YC API.

### Можно ли "поправить" изнутри задачи

Частично:
- ✅ Я могу валидировать состояние, подготовить команды, и сразу продолжить autodiscovery как только env появится.
- ❌ Я не могу изнутри контейнера создать/подключить secret в UI Codex за владельца окружения.

### Следующее действие (owner-side), затем сразу команда в задаче

1. В настройках окружения:
   - добавить/проверить secret `YC_TOKEN`;
   - добавить env `YC_FOLDER_ID=b1g42qj26s1u7gv7bufm`.
2. Нажать `Сбросить кэш` и пересоздать environment (новая задача/новый контейнер).
3. Если новый чат открыт, но контейнер всё равно старый — создать новый Codex Environment (другое имя/slug), потому что чат может переиспользовать кэш текущего environment.
4. В новой задаче выполнить:

```bash
printenv | rg '^YC_'
curl -sS -H "Authorization: Bearer $YC_TOKEN" \
  "https://resource-manager.api.cloud.yandex.net/resource-manager/v1/clouds?folderId=${YC_FOLDER_ID}"
```

---

## 8) Что нужно от владельца, чтобы я продолжил всё сам

Я могу выполнить autodiscovery полностью в этой задаче, но сейчас блокер только один: в runtime контейнер не проброшен `YC_TOKEN`.

Минимальная помощь от владельца окружения (1-2 минуты):

1. В настройках Codex Environment добавить/проверить:
   - Secret: `YC_TOKEN`;
   - Env: `YC_FOLDER_ID=b1g42qj26s1u7gv7bufm`.
2. Нажать **Сбросить кэш** и запустить новую задачу (новый контейнер).
3. Если не помогло — создать новый Codex Environment и добавить secret/env уже там.
4. Прислать одно подтверждение: вывод команды `printenv | rg '^YC_'` (без значения токена).

После этого я сразу делаю сам:

```bash
# 1) Проверка токена
curl -sS -H "Authorization: Bearer $YC_TOKEN" https://iam.api.cloud.yandex.net/iam/v1/tokens

# 2) Cloud/Folder
curl -sS -H "Authorization: Bearer $YC_TOKEN" \
  "https://resource-manager.api.cloud.yandex.net/resource-manager/v1/folders/${YC_FOLDER_ID}"

# 3) Service Accounts
curl -sS -H "Authorization: Bearer $YC_TOKEN" \
  "https://iam.api.cloud.yandex.net/iam/v1/serviceAccounts?folderId=${YC_FOLDER_ID}"

# 4) Functions
curl -sS -H "Authorization: Bearer $YC_TOKEN" \
  "https://serverless-functions.api.cloud.yandex.net/functions/v1/functions?folderId=${YC_FOLDER_ID}"

# 5) API Gateway
curl -sS -H "Authorization: Bearer $YC_TOKEN" \
  "https://serverless-apigateway.api.cloud.yandex.net/apigateways/v1/api-gateways?folderId=${YC_FOLDER_ID}"

# 6) Lockbox
curl -sS -H "Authorization: Bearer $YC_TOKEN" \
  "https://payload.lockbox.api.cloud.yandex.net/lockbox/v1/secrets?folderId=${YC_FOLDER_ID}"
```

