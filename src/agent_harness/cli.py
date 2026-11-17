"""Command-line entry point: run the agent on a task from the terminal.

Example::

    agent-harness "Read https://example.com and summarise it in one sentence." -v
"""

from __future__ import annotations

import argparse
import logging

from .agent import Agent
from .builtins import register_default_tools
from .config import build_client, load_settings
from .tools import ToolRegistry


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run a tool-calling agent on a task."
    )
    parser.add_argument("task", help="What you want the agent to do.")
    parser.add_argument(
        "--model",
        default=None,
        help="OpenRouter model id (default: openrouter/free).",
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=25,
        help="Maximum model calls before giving up (default: 25).",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show each step and tool call as it happens.",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(message)s",
    )

    settings = load_settings(model=args.model)
    client = build_client(settings)
    registry = register_default_tools(ToolRegistry())
    agent = Agent(client, registry, model=settings.model, max_steps=args.max_steps)

    answer = agent.run(args.task)
    print(answer)


if __name__ == "__main__":
    main()
