# Переменные окружения, секреты и доступы (Yandex Cloud)

Этот документ фиксирует, что нужно подготовить, чтобы агент мог **самостоятельно** делать деплой/обновления notify-gateway в Yandex Cloud.

## 1) Runtime переменные (в Cloud Function)

Обязательные:

- `NOTIFY_API_KEYS` (secret)  
  CSV ключей для Bearer-авторизации, пример: `key1,key2,key3`.
- `TELEGRAM_BOT_TOKEN` (secret)  
  Токен бота от BotFather.
- `TELEGRAM_CHAT_ID` (sensitive config)  
  Chat ID (личка/группа/канал), куда отправлять уведомления.

Рекомендованные дополнительные (опционально):

- `NOTIFY_MAX_MESSAGE_LEN` (config) — лимит длины `message`.
- `NOTIFY_MAX_EXTRA_LEN` (config) — лимит длины сериализованного `extra`.
- `LOG_LEVEL` (config) — уровень логирования (`INFO`, `DEBUG`, ...).

---

## 2) Deploy/CI переменные для работы с Yandex Cloud

Чтобы агент мог сам выполнять команды `yc ...`:

### Аутентификация (один из вариантов)
- `YC_TOKEN` (secret) — OAuth token для CLI, **или**
- `YC_IAM_TOKEN` (secret) — короткоживущий IAM token.

### Контекст
- `YC_CLOUD_ID` (config) — Cloud ID.
- `YC_FOLDER_ID` (config) — Folder ID, где ресурсы функции/API GW.

### Идентификаторы ресурсов
- `YC_FUNCTION_NAME` (config) — имя функции (например `notify-gateway`).
- `YC_FUNCTION_ID` (config) — ID функции (если уже создана).
- `YC_API_GW_NAME` (config) — имя API Gateway.
- `YC_API_GW_ID` (config) — ID API Gateway (если уже создан).
- `YC_SERVICE_ACCOUNT_ID` (config) — SA для вызова функции из API Gateway.

### Сеть/домен (опционально)
- `YC_DOMAIN` (config) — ваш домен для gateway.
- `YC_DNS_ZONE_ID` (config) — DNS zone ID (если автоматизируем DNS).

---

## 3) Минимальные роли в IAM

Для service account, под которым будет деплой/обновление:

- `serverless.functions.editor` — создавать/обновлять функцию.
- `api-gateway.editor` — создавать/обновлять API Gateway.
- `iam.serviceAccounts.user` — использовать service account при интеграциях.
- `logging.writer` — писать логи (если требуется отдельная роль).

Для service account интеграции API Gateway → Function:

- `serverless.functions.invoker` на целевую функцию.

> Точный набор ролей можно сузить после первого успешного деплоя (принцип least privilege).

---

## 4) Что нужно получить от владельца проекта до старта реализации

1. Значения:
   - `YC_CLOUD_ID`, `YC_FOLDER_ID`;
   - `YC_SERVICE_ACCOUNT_ID` (или право создать новый SA);
   - `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`;
   - начальный `NOTIFY_API_KEYS`.
2. Способ аутентификации агента в YC (`YC_TOKEN` или процесс выдачи IAM token).
3. Решение по домену (используем gateway URL или сразу custom domain).

---

## 5) Правила безопасности

- Никогда не коммитить секреты в git.
- Секреты хранить в CI/CD secret storage или YC Secret Manager.
- Минимум прав для SA и регулярная ротация токенов/ключей.
- Отдельные ключи для `dev/stage/prod` окружений.

---

## 6) Быстрый preflight-check перед деплоем

- [ ] `yc` CLI установлен и авторизован.
- [ ] Выбран `YC_CLOUD_ID` / `YC_FOLDER_ID`.
- [ ] Есть доступ на update/create Function и API Gateway.
- [ ] Проверен Telegram бот (`getMe`) и корректность `TELEGRAM_CHAT_ID`.
- [ ] Подготовлен набор runtime env vars.
