"""A handful of ready-made tools so the agent can do something out of the box.

These are deliberately small and general. Add your own tools the same way, or
register functions onto a fresh :class:`ToolRegistry` in your own script.
"""

from __future__ import annotations

import datetime as _dt

import requests
from bs4 import BeautifulSoup

from .tools import ToolRegistry


def read_web_page(url: str) -> str:
    """Fetch a web page and return its visible text with the HTML stripped out."""
    response = requests.get(
        url, timeout=20, headers={"User-Agent": "agent-harness/0.1"}
    )
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    body = soup.body or soup
    return body.get_text(separator="\n", strip=True)


def word_count(text: str) -> str:
    """Count the words and characters in a piece of text."""
    return f"{len(text.split())} words, {len(text)} characters"


def current_time() -> str:
    """Return the current local date and time in ISO 8601 format."""
    return _dt.datetime.now().isoformat(timespec="seconds")


def register_default_tools(registry: ToolRegistry) -> ToolRegistry:
    """Register the built-in example tools onto ``registry`` and return it."""
    registry.register(
        read_web_page,
        description="Fetch a web page and return its visible text, without HTML.",
        params={"url": "The full URL of the page to read, including https://"},
    )
    registry.register(
        word_count,
        description="Count the words and characters in a piece of text.",
        params={"text": "The text to measure."},
    )
    registry.register(
        current_time,
        description="Get the current date and time.",
    )
    return registry
