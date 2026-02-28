
# notify-gateway (Telegram Notification Gateway)

Небольшой HTTP-шлюз для отправки уведомлений в Telegram: проекты шлют POST в одну точку, а шлюз пересылает сообщение в чат через Telegram Bot API.

Цель: вынести телеграм-уведомления из каждого проекта в один сервис и деплоить его на **Yandex Cloud Functions** + **API Gateway** (serverless).

---

## MVP (что реализуем)

- `POST /notify` принимает JSON-событие
- авторизация через `Authorization: Bearer <API_KEY>`
- валидация входных данных
- отправка сообщения в Telegram (`sendMessage`)
- ответ JSON `{ "ok": true, ... }`

Дедуп/анти-спам — опционально (можно добавить позже через YDB).

---

## API

### Endpoint

`POST /notify`

### Headers

- `Content-Type: application/json`
- `Authorization: Bearer <API_KEY>`

### Body (JSON)

Поля:

- `project` (string, required) — имя проекта/сервиса
- `env` (string, optional, default: `"prod"`) — окружение
- `level` (string, optional, default: `"info"`) — `"info" | "warning" | "error"`
- `title` (string, required) — краткий заголовок
- `message` (string, required) — текст (может быть большим)
- `tags` (array[string], optional) — теги
- `extra` (object, optional) — любые доп. поля (request_id, host, commit, etc.)

Пример:

```json
{
  "project": "shadowgen-web",
  "env": "prod",
  "level": "error",
  "title": "Worker crashed",
  "message": "Traceback: ...",
  "tags": ["worker", "redis"],
  "extra": { "host": "vps-1", "commit": "a1b2c3d" }
}

Responses

200 OK — { "ok": true, "telegram_message_id": 123 }

400 Bad Request — { "ok": false, "error": "validation_error", "details": ... }

401 Unauthorized — { "ok": false, "error": "unauthorized" }

500 Internal Server Error — { "ok": false, "error": "internal_error" }



---

Telegram формат сообщения

Рекомендуемый формат (пример):

первая строка: emoji по уровню + project (env)

затем title

затем message

затем (если есть) tags и extra


Пример:

🟥 shadowgen-web (prod)
Worker crashed
Traceback: ...

tags: worker, redis
extra: host=vps-1, commit=a1b2c3d

Parse mode: предпочтительно HTML (меньше боли, чем MarkdownV2).


---

Конфигурация через переменные окружения

Обязательные:

TG_BOT_TOKEN — токен бота Telegram

TG_CHAT_ID — chat_id куда слать (личка/группа/канал)

NOTIFY_API_KEYS — ключи доступа


Формат NOTIFY_API_KEYS

В MVP допускаем простой CSV со списком ключей:

NOTIFY_API_KEYS=key1,key2,key3

(Позже можно расширить до JSON-map project -> key.)


---

Пример запроса (curl)

curl -X POST "https://<YOUR_DOMAIN>/notify" \
  -H "Authorization: Bearer key1" \
  -H "Content-Type: application/json" \
  -d '{
    "project": "shadowgen",
    "env": "prod",
    "level": "error",
    "title": "Crash",
    "message": "Something went wrong"
  }'


---

Подсказки по деплою в Yandex Cloud (в общих чертах)

1. Создать Telegram-бота (BotFather), получить TG_BOT_TOKEN.


2. Узнать TG_CHAT_ID (или добавить бота в группу/канал).


3. Создать Cloud Function (Python 3.11), добавить env vars.


4. Создать API Gateway и маршрут POST /notify → Cloud Function.


5. Привязать домен к API Gateway (опционально).




---

Чеклист готовности

[ ] Функция принимает POST /notify

[ ] Проверяет Bearer API key

[ ] Валидирует JSON

[ ] Отправляет сообщение в Telegram

[ ] Возвращает понятный JSON-ответ

[ ] Секреты только в env, не в репозитории



---

Future (потом)

дедуп/анти-спам (YDB serverless, TTL по fingerprint)

маршрутизация по проектам → разные chat_id/thread

HMAC подпись вместо Bearer key

приоритеты, батчинг, summary-уведомления
