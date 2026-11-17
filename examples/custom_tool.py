"""Register your own tool and let the agent use it.

Shows the whole point of the registry: any plain function becomes a tool with
one decorator, and the agent decides when to call it.

    python examples/custom_tool.py
"""

from __future__ import annotations

from agent_harness import Agent, ToolRegistry, build_client, load_settings

registry = ToolRegistry()


@registry.register(
    description="Add two numbers together.",
    params={"a": "the first number", "b": "the second number"},
)
def add(a: float, b: float) -> str:
    return str(a + b)


def main() -> None:
    settings = load_settings()
    client = build_client(settings)
    agent = Agent(client, registry, model=settings.model)
    print(agent.run("What is 2024 plus 1? Use your tool to be sure."))


if __name__ == "__main__":
    main()
