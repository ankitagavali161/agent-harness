"""Configuration and client construction.

Credentials live in a ``.env`` file (never in code). This module reads the
OpenRouter API key, bundles the connection settings into one immutable object,
and builds an OpenAI-compatible client pointed at OpenRouter.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv
from openai import OpenAI

# OpenRouter speaks the OpenAI API, so we reuse the OpenAI client and only
# change the base URL. "openrouter/free" routes each request to whichever free
# model is available, which is handy for experiments that make many calls.
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "openrouter/free"


@dataclass(frozen=True)
class Settings:
    """Everything needed to talk to the model, in one place."""

    api_key: str
    base_url: str = OPENROUTER_BASE_URL
    model: str = DEFAULT_MODEL
    timeout: int = 120
    max_retries: int = 5


def load_settings(model: str | None = None) -> Settings:
    """Read the API key from ``.env`` and return the connection settings.

    Raises a clear error if the key is missing so the problem is obvious.
    """
    load_dotenv(override=True)
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENROUTER_API_KEY is not set. Copy .env.example to .env and add your key."
        )
    return Settings(api_key=api_key, model=model or DEFAULT_MODEL)


def build_client(settings: Settings) -> OpenAI:
    """Create an OpenAI-compatible client pointed at OpenRouter."""
    return OpenAI(
        base_url=settings.base_url,
        api_key=settings.api_key,
        timeout=settings.timeout,
        max_retries=settings.max_retries,
    )
