import pytest

from openai_mcp import server


class _FakeResponses:
    def __init__(self, calls):
        self._calls = calls

    def create(self, **kwargs):
        self._calls.append(kwargs)

        class _Resp:
            output_text = "fake answer"

        return _Resp()


class _FakeOpenAI:
    calls: list = []

    def __init__(self, *args, **kwargs):
        self.responses = _FakeResponses(_FakeOpenAI.calls)


@pytest.fixture
def calls(monkeypatch):
    _FakeOpenAI.calls = []
    monkeypatch.setattr(server, "OpenAI", _FakeOpenAI)
    for var in (
        "OPENAI_MODELS",
        "OPENAI_DEFAULT_MODEL",
        "OPENAI_REASONING_MODELS",
        "OPENAI_REASONING_EFFORT",
        "OPENAI_ASK_REASONING_EFFORT",
        "OPENAI_SEARCH_CONTEXT_SIZE",
    ):
        monkeypatch.delenv(var, raising=False)
    return _FakeOpenAI.calls


# --- openai_web_search (existing behavior, pinned down) ---

def test_web_search_defaults_to_low_effort_and_default_model(calls):
    server.openai_web_search(input="hello")
    req = calls[0]
    assert req["model"] == server.DEFAULT_MODELS[0]
    assert req["reasoning"] == {"effort": "low"}
    assert req["tools"][0]["type"] == "web_search"


def test_web_search_global_env_override_applies(calls, monkeypatch):
    monkeypatch.setenv("OPENAI_REASONING_EFFORT", "high")
    server.openai_web_search(input="hello", reasoning_effort="low")
    assert calls[0]["reasoning"] == {"effort": "high"}


# --- openai_ask ---

def test_ask_defaults_to_medium_effort_and_default_model(calls):
    server.openai_ask(input="how should I structure this?")
    req = calls[0]
    assert req["model"] == server.DEFAULT_MODELS[0]
    assert req["reasoning"] == {"effort": "medium"}


def test_ask_attaches_web_search_tool_but_does_not_instruct_searching(calls):
    server.openai_ask(input="ideas for a CLI")
    req = calls[0]
    assert any(t["type"] == "web_search" for t in req["tools"])
    assert "search" not in req["instructions"].lower()
    assert "web" not in req["instructions"].lower()


def test_ask_returns_model_output_text(calls):
    assert server.openai_ask(input="x") == "fake answer"


def test_ask_includes_context_and_input_in_request(calls):
    server.openai_ask(input="name this product", context="It is a CLI for deploys")
    payload = str(calls[0]["input"])
    assert "name this product" in payload
    assert "It is a CLI for deploys" in payload


def test_ask_without_context_sends_plain_input(calls):
    server.openai_ask(input="just the question")
    assert calls[0]["input"] == "just the question"


def test_ask_per_request_effort_is_honoured(calls):
    server.openai_ask(input="x", reasoning_effort="high")
    assert calls[0]["reasoning"] == {"effort": "high"}


def test_ask_env_override_wins_over_request_param(calls, monkeypatch):
    monkeypatch.setenv("OPENAI_ASK_REASONING_EFFORT", "low")
    server.openai_ask(input="x", reasoning_effort="high")
    assert calls[0]["reasoning"] == {"effort": "low"}


def test_ask_ignores_web_search_effort_env_var(calls, monkeypatch):
    monkeypatch.setenv("OPENAI_REASONING_EFFORT", "low")
    server.openai_ask(input="x")
    assert calls[0]["reasoning"] == {"effort": "medium"}


def test_ask_omits_reasoning_when_reasoning_models_disabled(calls, monkeypatch):
    monkeypatch.setenv("OPENAI_REASONING_MODELS", "")
    server.openai_ask(input="x")
    assert "reasoning" not in calls[0]


def test_ask_rejects_model_not_in_allowlist(calls, monkeypatch):
    monkeypatch.setenv("OPENAI_MODELS", "gpt-5.6-sol")
    result = server.openai_ask(input="x", model="gpt-4o")
    assert result.startswith("Error:")
    assert "gpt-4o" in result
    assert calls == []


def test_ask_uses_default_model_env_var(calls, monkeypatch):
    monkeypatch.setenv("OPENAI_MODELS", "gpt-5.6-sol,gpt-5.6-terra")
    monkeypatch.setenv("OPENAI_DEFAULT_MODEL", "gpt-5.6-terra")
    server.openai_ask(input="x")
    assert calls[0]["model"] == "gpt-5.6-terra"


# --- error surfacing: API failures must reach the model as ToolError text ---

class _FailingOpenAI:
    def __init__(self, *args, **kwargs):
        import httpx2 as httpx
        import openai

        class _R:
            def create(self, **kwargs):
                request = httpx.Request("POST", "https://api.openai.com/v1/responses")
                response = httpx.Response(401, request=request, json={"error": {"message": "Incorrect API key provided"}})
                raise openai.AuthenticationError("Incorrect API key provided", response=response, body=None)

        self.responses = _R()


@pytest.fixture
def failing_client(monkeypatch):
    monkeypatch.setattr(server, "OpenAI", _FailingOpenAI)
    for var in ("OPENAI_MODELS", "OPENAI_DEFAULT_MODEL", "OPENAI_REASONING_MODELS"):
        monkeypatch.delenv(var, raising=False)


def test_web_search_api_error_is_raised_as_tool_error_with_message(failing_client):
    from mcp.server.mcpserver.exceptions import ToolError

    with pytest.raises(ToolError) as exc_info:
        server.openai_web_search(input="hello")
    assert "Incorrect API key provided" in str(exc_info.value)
    assert "401" in str(exc_info.value)


def test_ask_api_error_is_raised_as_tool_error_with_message(failing_client):
    from mcp.server.mcpserver.exceptions import ToolError

    with pytest.raises(ToolError) as exc_info:
        server.openai_ask(input="hello")
    assert "Incorrect API key provided" in str(exc_info.value)
