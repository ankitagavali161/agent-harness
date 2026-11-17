"""A small tool registry that turns plain Python functions into LLM tools.

The model never runs our code. We describe each function to it as JSON; when the
model asks for a function by name, we run the real Python and feed the result
back into the conversation.

Writing that JSON by hand (and keeping it in sync with the function) is tedious
and error-prone, so this registry builds the schema from the function's own
signature and docstring. Registering a tool is then a single decorator.
"""

from __future__ import annotations

import inspect
import json
import logging
from dataclasses import dataclass, field
from typing import Any, Callable

logger = logging.getLogger(__name__)

# How Python type hints map onto JSON Schema types. Anything unknown falls back
# to "string", which the model can still work with.
_PYTHON_TO_JSON = {
    str: "string",
    int: "integer",
    float: "number",
    bool: "boolean",
    list: "array",
    dict: "object",
}


@dataclass
class Tool:
    """A single callable paired with the metadata the model needs to use it."""

    func: Callable[..., Any]
    name: str
    description: str
    param_descriptions: dict[str, str] = field(default_factory=dict)

    @property
    def schema(self) -> dict:
        """Build the JSON description the model reads to decide when to call this tool."""
        properties: dict[str, dict] = {}
        required: list[str] = []
        # eval_str=True resolves string annotations (produced by
        # ``from __future__ import annotations``) back into real types.
        try:
            signature = inspect.signature(self.func, eval_str=True)
        except (NameError, TypeError):
            signature = inspect.signature(self.func)
        for pname, param in signature.parameters.items():
            json_type = _PYTHON_TO_JSON.get(param.annotation, "string")
            properties[pname] = {
                "type": json_type,
                "description": self.param_descriptions.get(pname, ""),
            }
            # A parameter with no default value is required.
            if param.default is inspect.Parameter.empty:
                required.append(pname)
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            },
        }

    def __call__(self, **kwargs: Any) -> Any:
        return self.func(**kwargs)


class ToolRegistry:
    """Holds the tools an agent can use and dispatches the model's calls to them."""

    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(
        self,
        _func: Callable[..., Any] | None = None,
        *,
        name: str | None = None,
        description: str | None = None,
        params: dict[str, str] | None = None,
    ):
        """Register a function as a tool.

        Works both bare (``@registry.register``) and with arguments
        (``@registry.register(description=..., params={...})``). The function
        stays a normal callable so it can still be imported and tested directly.
        """

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            tool = Tool(
                func=func,
                name=name or func.__name__,
                description=description or (inspect.getdoc(func) or "").strip(),
                param_descriptions=params or {},
            )
            self._tools[tool.name] = tool
            return func

        if _func is not None:
            return decorator(_func)
        return decorator

    @property
    def schemas(self) -> list[dict]:
        """All tool schemas, in the shape the chat API expects."""
        return [tool.schema for tool in self._tools.values()]

    def dispatch(self, tool_call: Any) -> dict:
        """Run the tool the model asked for and package the result as a message.

        Any failure (bad JSON, unknown tool, an exception inside the tool) is
        turned into a plain-text result and handed back to the model, so it can
        read the error and try something else instead of the whole run crashing.
        """
        name = tool_call.function.name
        try:
            arguments = json.loads(tool_call.function.arguments or "{}")
            tool = self._tools[name]
            logger.info("Calling tool %s(%s)", name, arguments)
            result = tool(**arguments)
        except KeyError:
            result = f"No tool named {name!r} is available."
        except Exception as error:  # noqa: BLE001 - deliberately fed back to the model
            result = f"The tool call failed: {error}"
        return {"role": "tool", "tool_call_id": tool_call.id, "content": str(result)}

    def __len__(self) -> int:
        return len(self._tools)

    def __contains__(self, name: str) -> bool:
        return name in self._tools
