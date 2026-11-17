"""Tests for the tool registry. These are pure: no network, no API key."""

from __future__ import annotations

import json
from types import SimpleNamespace

from agent_harness import ToolRegistry


def fake_tool_call(call_id: str, name: str, arguments: str) -> SimpleNamespace:
    """Mimic the shape of an OpenAI tool_call object."""
    return SimpleNamespace(
        id=call_id,
        function=SimpleNamespace(name=name, arguments=arguments),
    )


def test_schema_is_built_from_signature() -> None:
    registry = ToolRegistry()

    @registry.register(description="Echo text.", params={"text": "the text"})
    def echo(text: str, times: int = 1) -> str:
        return text * times

    function = registry.schemas[0]["function"]
    assert function["name"] == "echo"
    assert function["description"] == "Echo text."

    properties = function["parameters"]["properties"]
    assert properties["text"]["type"] == "string"
    assert properties["times"]["type"] == "integer"
    assert properties["text"]["description"] == "the text"
    # `times` has a default, so it is optional; `text` is required.
    assert function["parameters"]["required"] == ["text"]


def test_description_defaults_to_docstring() -> None:
    registry = ToolRegistry()

    @registry.register()
    def greet(name: str) -> str:
        """Say hello to someone."""
        return f"hello {name}"

    assert registry.schemas[0]["function"]["description"] == "Say hello to someone."


def test_dispatch_runs_the_tool() -> None:
    registry = ToolRegistry()

    @registry.register()
    def add(a: int, b: int) -> int:
        return a + b

    message = registry.dispatch(
        fake_tool_call("1", "add", json.dumps({"a": 2, "b": 3}))
    )
    assert message == {"role": "tool", "tool_call_id": "1", "content": "5"}


def test_dispatch_reports_tool_errors_instead_of_raising() -> None:
    registry = ToolRegistry()

    @registry.register()
    def boom() -> str:
        raise ValueError("nope")

    message = registry.dispatch(fake_tool_call("2", "boom", "{}"))
    assert "failed" in message["content"]


def test_dispatch_handles_unknown_tool() -> None:
    registry = ToolRegistry()
    message = registry.dispatch(fake_tool_call("3", "ghost", "{}"))
    assert "No tool named" in message["content"]
