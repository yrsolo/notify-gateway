import json
from urllib import request

import handler


def _event(body: dict, auth_header: str | None = "Bearer test-key") -> dict:
    headers = {}
    if auth_header is not None:
        headers["Authorization"] = auth_header
    return {
        "headers": headers,
        "body": json.dumps(body),
    }


def test_unauthorized_when_api_key_invalid(monkeypatch):
    monkeypatch.setenv("NOTIFY_API_KEYS", "test-key")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "chat")

    event = _event(
        {
            "project": "proj",
            "title": "title",
            "message": "message",
        },
        auth_header="Bearer wrong",
    )

    result = handler.handler(event, None)

    assert result["statusCode"] == 401
    assert json.loads(result["body"]) == {"ok": False, "error": "invalid API key"}


def test_bad_request_when_payload_invalid(monkeypatch):
    monkeypatch.setenv("NOTIFY_API_KEYS", "test-key")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "chat")

    event = _event({"project": "proj", "title": "title"})

    result = handler.handler(event, None)

    assert result["statusCode"] == 400
    assert "field 'message' is required" in json.loads(result["body"])["error"]


def test_successful_send(monkeypatch):
    monkeypatch.setenv("NOTIFY_API_KEYS", "test-key")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "chat")

    captured = {}

    class _FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            return False

        def read(self):
            return json.dumps({"ok": True, "result": {"message_id": 777}}).encode("utf-8")

    def _fake_urlopen(req, timeout):
        captured["url"] = req.full_url
        captured["timeout"] = timeout
        payload = json.loads(req.data.decode("utf-8"))
        captured["payload"] = payload
        return _FakeResponse()

    monkeypatch.setattr(request, "urlopen", _fake_urlopen)

    event = _event(
        {
            "project": "billing",
            "env": "staging",
            "level": "warning",
            "title": "Lag spike",
            "message": "Queue > 1k",
            "tags": ["queue", "worker"],
            "extra": {"lag": 1500},
        }
    )

    result = handler.handler(event, None)

    assert result["statusCode"] == 200
    assert json.loads(result["body"]) == {"ok": True, "telegram_message_id": 777}
    assert captured["url"] == "https://api.telegram.org/bottoken/sendMessage"
    assert captured["payload"]["chat_id"] == "chat"
    assert captured["payload"]["parse_mode"] == "HTML"
    assert "🟨 billing (staging)" in captured["payload"]["text"]
