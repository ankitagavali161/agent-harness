"""Tests for the agent loop, using a scripted fake client (no network)."""

from __future__ import annotations

from types import SimpleNamespace

from agent_harness import Agent, ToolRegistry


def make_message(content=None, tool_calls=None) -> SimpleNamespace:
    return SimpleNamespace(content=content, tool_calls=tool_calls)


def make_response(message, model="fake-model") -> SimpleNamespace:
    return SimpleNamespace(
        model=model,
        choices=[SimpleNamespace(message=message, finish_reason="stop")],
    )


class ScriptedClient:
    """Returns a queued list of responses, one per create() call, and records calls."""

    def __init__(self, responses):
        self._responses = list(responses)
        self.calls: list[dict] = []
        self.chat = SimpleNamespace(
            completions=SimpleNamespace(create=self._create)
        )

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        return self._responses.pop(0)


def test_agent_runs_tool_then_returns_final_answer() -> None:
    registry = ToolRegistry()

    @registry.register()
    def ping() -> str:
        return "pong"

    tool_call = SimpleNamespace(
        id="1", function=SimpleNamespace(name="ping", arguments="{}")
    )
    client = ScriptedClient(
        [
            make_response(make_message(content=None, tool_calls=[tool_call])),
            make_response(make_message(content="All done", tool_calls=None)),
        ]
    )

    agent = Agent(client, registry, model="x", max_steps=5)
    answer = agent.run("do the thing")

    assert answer == "All done"
    assert agent.steps_taken == 2

    # The tool result must have been fed back into the second model call.
    second_call_messages = client.calls[1]["messages"]
    tool_messages = [m for m in second_call_messages if isinstance(m, dict)]
    assert any(
        m.get("role") == "tool" and m["content"] == "pong" for m in tool_messages
    )


def test_agent_gives_up_after_max_steps() -> None:
    registry = ToolRegistry()
    # Always reply empty: never a tool call, never text.
    empty = make_message(content=None, tool_calls=None)
    client = ScriptedClient([make_response(empty) for _ in range(10)])

    agent = Agent(client, registry, model="x", max_steps=3)
    answer = agent.run("impossible")

    assert answer == ""
    assert agent.steps_taken == 3
