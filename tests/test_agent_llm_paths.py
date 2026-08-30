from types import SimpleNamespace

import pytest

import nova.agents.base_agent as base_agent_module
import nova.llm.client as llm_client


class FakeMessage:
    def __init__(self, content="Final answer", tool_calls=None, role="assistant"):
        self.content = content
        self.tool_calls = tool_calls or []
        self.role = role


class FakeResponse:
    def __init__(self, message):
        self.choices = [SimpleNamespace(message=message)]


def test_base_agent_uses_fallback_client(monkeypatch):
    calls = {}

    def fake_completion_with_fallback(**kwargs):
        calls["kwargs"] = kwargs
        return FakeResponse(FakeMessage(content="Done"))

    monkeypatch.setattr(base_agent_module, "completion_with_fallback", fake_completion_with_fallback)

    agent = base_agent_module.BaseAgent(
        name="Test Agent",
        system_prompt="You are helpful.",
        tools=[],
    )

    result = agent.run("What is the status?")

    assert result == "Done"
    assert calls["kwargs"]["messages"][0]["role"] == "system"
    assert calls["kwargs"]["tools"] == []
    assert "tool_choice" not in calls["kwargs"]


def test_completion_with_fallback_defaults_tool_choice_for_tools(monkeypatch):
    monkeypatch.setattr(llm_client, "GROQ_MODEL", "llama-3.1-8b")
    monkeypatch.setattr(llm_client, "GROQ_API_KEY", "groq-secret")
    monkeypatch.setattr(llm_client, "GEMINI_MODEL", "gemini-1.5-flash")
    monkeypatch.setattr(llm_client, "GEMINI_API_KEY", "gemini-secret")

    seen = {}

    def fake_completion(**kwargs):
        seen["calls"] = seen.get("calls", []) + [kwargs]
        if kwargs["model"].startswith("groq/"):
            raise RuntimeError("primary error")
        return FakeResponse(FakeMessage(content="fallback with auto tool choice"))

    monkeypatch.setattr(llm_client, "completion", fake_completion)

    result = llm_client.completion_with_fallback(
        messages=[{"role": "user", "content": "hi"}],
        tools=[{"type": "function", "function": {"name": "demo"}}],
    )

    assert result.choices[0].message.content == "fallback with auto tool choice"
    assert seen["calls"][0]["tool_choice"] == "auto"
    assert seen["calls"][1]["tool_choice"] == "auto"


def test_ask_llm_routes_through_completion_with_fallback(monkeypatch):
    observed = {}

    def fake_completion_with_fallback(**kwargs):
        observed["kwargs"] = kwargs
        return FakeResponse(FakeMessage(content="fallback result"))

    def fail_completion(**_kwargs):
        raise AssertionError("Direct litellm completion should not be used here")

    monkeypatch.setattr(llm_client, "completion_with_fallback", fake_completion_with_fallback)
    monkeypatch.setattr(llm_client, "completion", fail_completion)

    result = llm_client.ask_llm("system prompt", "user prompt")

    assert result == "fallback result"
    assert observed["kwargs"]["messages"][0]["role"] == "system"
    assert observed["kwargs"]["messages"][1]["role"] == "user"


def test_completion_with_fallback_uses_gemini_and_forwards_max_tokens(monkeypatch):
    monkeypatch.setattr(llm_client, "GROQ_MODEL", "llama-3.1-8b")
    monkeypatch.setattr(llm_client, "GROQ_API_KEY", "groq-secret")
    monkeypatch.setattr(llm_client, "GEMINI_MODEL", "gemini-1.5-flash")
    monkeypatch.setattr(llm_client, "GEMINI_API_KEY", "gemini-secret")

    calls = []

    def fake_completion(**kwargs):
        calls.append(kwargs)
        if kwargs["model"].startswith("groq/"):
            raise RuntimeError("primary groq error")
        return FakeResponse(FakeMessage(content="gemini fallback result"))

    monkeypatch.setattr(llm_client, "completion", fake_completion)

    result = llm_client.completion_with_fallback(
        messages=[{"role": "user", "content": "hi"}],
        max_tokens=512,
    )

    assert result.choices[0].message.content == "gemini fallback result"
    assert len(calls) == 2
    assert calls[0]["max_tokens"] == 512
    assert calls[1]["max_tokens"] == 512


def test_completion_with_fallback_raises_clean_fallback_exception(monkeypatch):
    monkeypatch.setattr(llm_client, "GROQ_MODEL", "llama-3.1-8b")
    monkeypatch.setattr(llm_client, "GROQ_API_KEY", "groq-secret")
    monkeypatch.setattr(llm_client, "GEMINI_MODEL", "gemini-1.5-flash")
    monkeypatch.setattr(llm_client, "GEMINI_API_KEY", "gemini-secret")

    def fake_completion(**kwargs):
        if kwargs["model"].startswith("groq/"):
            raise RuntimeError("Groq outage")
        raise RuntimeError("Gemini outage")

    monkeypatch.setattr(llm_client, "completion", fake_completion)

    with pytest.raises(llm_client.FallbackLLMFailure) as exc_info:
        llm_client.completion_with_fallback(messages=[{"role": "user", "content": "hi"}])

    assert exc_info.value.primary_exception is not None
    assert exc_info.value.fallback_exception is not None
    assert "Gemini" in str(exc_info.value)
