"""Run the same task against several models and compare how many steps each takes.

Because the harness is model-agnostic, the model id is the only thing that
changes between runs. This script makes that point measurable.

    python examples/compare_models.py
"""

from __future__ import annotations

import logging

from agent_harness import (
    Agent,
    ToolRegistry,
    build_client,
    load_settings,
    register_default_tools,
)

MODELS = [
    "openrouter/free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "google/gemini-2.0-flash-exp:free",
]

TASK = "Read https://example.com and tell me in one sentence what the page is for."


def main() -> None:
    logging.basicConfig(level=logging.WARNING, format="%(message)s")
    settings = load_settings()
    client = build_client(settings)
    registry = register_default_tools(ToolRegistry())

    print(f"Task: {TASK}\n")
    for model in MODELS:
        agent = Agent(client, registry, model=model, max_steps=15)
        try:
            answer = agent.run(TASK)
            summary = (answer or "(no answer)").replace("\n", " ")[:80]
            print(f"{model:<45} {agent.steps_taken:>2} steps  | {summary}")
        except Exception as error:  # noqa: BLE001 - keep comparing the other models
            print(f"{model:<45}  -- failed: {error}")


if __name__ == "__main__":
    main()
