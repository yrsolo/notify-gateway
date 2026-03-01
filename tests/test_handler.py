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


def test_template_raw_uses_plain_message(monkeypatch):
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
            return json.dumps({"ok": True, "result": {"message_id": 778}}).encode("utf-8")

    def _fake_urlopen(req, timeout):
        del timeout
        payload = json.loads(req.data.decode("utf-8"))
        captured["text"] = payload["text"]
        return _FakeResponse()

    monkeypatch.setattr(request, "urlopen", _fake_urlopen)

    event = _event(
        {
            "project": "billing",
            "title": "Any title",
            "message": "raw <b>text</b>",
            "template": "raw",
        }
    )

    result = handler.handler(event, None)

    assert result["statusCode"] == 200
    assert captured["text"] == "raw &lt;b&gt;text&lt;/b&gt;"


def test_template_error_uses_error_header(monkeypatch):
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
            return json.dumps({"ok": True, "result": {"message_id": 779}}).encode("utf-8")

    def _fake_urlopen(req, timeout):
        del timeout
        payload = json.loads(req.data.decode("utf-8"))
        captured["text"] = payload["text"]
        return _FakeResponse()

    monkeypatch.setattr(request, "urlopen", _fake_urlopen)

    event = _event(
        {
            "project": "billing",
            "env": "prod",
            "title": "DB unavailable",
            "message": "Connection timeout",
            "template": "error",
            "tags": ["db"],
            "extra": {"retry": 3},
        }
    )

    result = handler.handler(event, None)

    assert result["statusCode"] == 200
    assert "🚨 <b>ERROR</b> billing (prod)" in captured["text"]
    assert "<i>context:</i> retry=3" in captured["text"]


def test_bad_request_when_template_invalid(monkeypatch):
    monkeypatch.setenv("NOTIFY_API_KEYS", "test-key")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "chat")

    event = _event(
        {
            "project": "proj",
            "title": "title",
            "message": "message",
            "template": "unknown",
        }
    )

    result = handler.handler(event, None)

    assert result["statusCode"] == 400
    assert "field 'template' must be one of" in json.loads(result["body"])["error"]


def test_chat_id_override_routes_to_custom_chat(monkeypatch):
    monkeypatch.setenv("NOTIFY_API_KEYS", "test-key")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "default-chat")

    captured = {}

    class _FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            return False

        def read(self):
            return json.dumps({"ok": True, "result": {"message_id": 780}}).encode("utf-8")

    def _fake_urlopen(req, timeout):
        del timeout
        payload = json.loads(req.data.decode("utf-8"))
        captured["chat_id"] = payload["chat_id"]
        return _FakeResponse()

    monkeypatch.setattr(request, "urlopen", _fake_urlopen)

    event = _event(
        {
            "project": "billing",
            "title": "Lag",
            "message": "msg",
            "chat_id": "-100123456789",
        }
    )

    result = handler.handler(event, None)

    assert result["statusCode"] == 200
    assert captured["chat_id"] == "-100123456789"



def test_chat_alias_routes_to_mapped_chat(monkeypatch):
    monkeypatch.setenv("NOTIFY_API_KEYS", "test-key")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "default-chat")
    monkeypatch.setenv("TELEGRAM_CHAT_ALIASES", "ops=-10010,alerts=@alerts_room")

    captured = {}

    class _FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            return False

        def read(self):
            return json.dumps({"ok": True, "result": {"message_id": 781}}).encode("utf-8")

    def _fake_urlopen(req, timeout):
        del timeout
        payload = json.loads(req.data.decode("utf-8"))
        captured["chat_id"] = payload["chat_id"]
        return _FakeResponse()

    monkeypatch.setattr(request, "urlopen", _fake_urlopen)

    event = _event(
        {
            "project": "billing",
            "title": "Lag",
            "message": "msg",
            "chat_alias": "ops",
        }
    )

    result = handler.handler(event, None)

    assert result["statusCode"] == 200
    assert captured["chat_id"] == "-10010"



def test_default_chat_used_when_no_override(monkeypatch):
    monkeypatch.setenv("NOTIFY_API_KEYS", "test-key")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "default-chat")
    monkeypatch.setenv("TELEGRAM_CHAT_ALIASES", "ops=-10010")

    captured = {}

    class _FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            return False

        def read(self):
            return json.dumps({"ok": True, "result": {"message_id": 782}}).encode("utf-8")

    def _fake_urlopen(req, timeout):
        del timeout
        payload = json.loads(req.data.decode("utf-8"))
        captured["chat_id"] = payload["chat_id"]
        return _FakeResponse()

    monkeypatch.setattr(request, "urlopen", _fake_urlopen)

    event = _event(
        {
            "project": "billing",
            "title": "Lag",
            "message": "msg",
        }
    )

    result = handler.handler(event, None)

    assert result["statusCode"] == 200
    assert captured["chat_id"] == "default-chat"



def test_bad_request_for_unknown_chat_alias(monkeypatch):
    monkeypatch.setenv("NOTIFY_API_KEYS", "test-key")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "default-chat")
    monkeypatch.setenv("TELEGRAM_CHAT_ALIASES", "ops=-10010")

    event = _event(
        {
            "project": "billing",
            "title": "Lag",
            "message": "msg",
            "chat_alias": "unknown",
        }
    )

    result = handler.handler(event, None)

    assert result["statusCode"] == 400
    assert "unknown chat alias" in json.loads(result["body"])["error"]



def test_bad_request_when_chat_override_and_alias_both_set(monkeypatch):
    monkeypatch.setenv("NOTIFY_API_KEYS", "test-key")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "default-chat")

    event = _event(
        {
            "project": "billing",
            "title": "Lag",
            "message": "msg",
            "chat_id": "-10010",
            "chat_alias": "ops",
        }
    )

    result = handler.handler(event, None)

    assert result["statusCode"] == 400
    assert "mutually exclusive" in json.loads(result["body"])["error"]



def test_server_error_when_aliases_env_invalid(monkeypatch):
    monkeypatch.setenv("NOTIFY_API_KEYS", "test-key")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "default-chat")
    monkeypatch.setenv("TELEGRAM_CHAT_ALIASES", "ops")

    event = _event(
        {
            "project": "billing",
            "title": "Lag",
            "message": "msg",
        }
    )

    result = handler.handler(event, None)

    assert result["statusCode"] == 500
    assert "invalid TELEGRAM_CHAT_ALIASES format" in json.loads(result["body"])["error"]


def test_help_mode_via_get_path_without_auth():
    event = {
        "httpMethod": "GET",
        "path": "/notify/help",
        "headers": {},
        "body": "",
    }

    result = handler.handler(event, None)

    assert result["statusCode"] == 200
    body = json.loads(result["body"])
    assert body["ok"] is True
    assert body["usage"] == "POST /notify"
    assert "project" in body["required_fields"]



def test_help_mode_via_payload_flag_without_auth():
    event = {
        "headers": {},
        "body": json.dumps({"help": True}),
    }

    result = handler.handler(event, None)

    assert result["statusCode"] == 200
    body = json.loads(result["body"])
    assert body["ok"] is True
    assert "minimal" in body["examples"]
