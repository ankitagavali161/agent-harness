"""A tiny, model-agnostic agent harness built around LLM tool calling."""

from .agent import DEFAULT_SYSTEM_PROMPT, Agent
from .builtins import register_default_tools
from .config import Settings, build_client, load_settings
from .tools import Tool, ToolRegistry

__all__ = [
    "Agent",
    "DEFAULT_SYSTEM_PROMPT",
    "Settings",
    "build_client",
    "load_settings",
    "Tool",
    "ToolRegistry",
    "register_default_tools",
]
__version__ = "0.1.0"
