"""The agent harness: call the model in a loop, running tools until it answers.

This is the heart of the project. The model cannot act on the world on its own,
so we wrap it in a loop:

1. Send the conversation (plus the list of tools) to the model.
2. If the model asks to use tools, run them and append the results.
3. If the model replies with text and no tool call, that is the final answer.

The orchestration lives here, in our code, not in the model. That is why the
same harness works with any model that supports tool calling.
"""

from __future__ import annotations

import logging

from .tools import ToolRegistry

logger = logging.getLogger(__name__)

DEFAULT_SYSTEM_PROMPT = (
    "You are a careful assistant that completes tasks step by step using the tools "
    "you are given. Call one tool at a time, read the result, then decide what to do "
    "next. When you are finished, reply in Markdown with a short, clear summary and "
    "stop calling tools."
)


class Agent:
    """Runs a task by calling a model in a tool-using loop."""

    def __init__(
        self,
        client,
        registry: ToolRegistry,
        model: str = "openrouter/free",
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
        max_steps: int = 25,
    ) -> None:
        self.client = client
        self.registry = registry
        self.model = model
        self.system_prompt = system_prompt
        self.max_steps = max_steps
        # Number of model calls the last run() took. Useful for comparing models.
        self.steps_taken = 0

    def run(self, task: str) -> str:
        """Work on ``task`` until the model gives a final text answer.

        Returns that answer, or an empty string if the agent runs out of steps.
        """
        messages: list = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": task},
        ]
        self.steps_taken = 0

        for step in range(1, self.max_steps + 1):
            self.steps_taken = step
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.registry.schemas or None,
            )
            message = response.choices[0].message
            text = (message.content or "").strip()
            logger.info("Step %d answered by %s", step, response.model)
            if text:
                logger.info("Model: %s", text)

            if message.tool_calls:
                # Record the model's request, then every tool result, so the next
                # call sees the full history.
                messages.append(message)
                for tool_call in message.tool_calls:
                    messages.append(self.registry.dispatch(tool_call))
                continue

            if text:
                return text

            # Small free models occasionally return nothing; just ask again.
            logger.warning("Empty reply with no tool call; asking again.")

        logger.warning("Agent hit max_steps=%d without a final answer.", self.max_steps)
        return ""
