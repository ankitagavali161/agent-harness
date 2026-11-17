# agent-harness

A tiny, model-agnostic **agent harness** built from first principles to understand
how LLM *tool calling* actually works — the loop that lets a language model use
real Python functions to get things done.

A language model can only produce text. On its own it cannot read a web page,
check the time, or do arithmetic reliably. An *agent harness* is the code around
the model that closes that gap:

1. We describe our Python functions to the model as JSON "tools".
2. The model replies asking to call a tool, with arguments.
3. **Our code** runs the real function and feeds the result back.
4. We loop until the model stops asking for tools and gives a final answer.

The important idea: the orchestration lives in *our* code, not the model. That is
why the same harness works with any model that supports tool calling — you can
swap the model id and nothing else changes.

## Features

- **Tool registry** — turn any Python function into a model-callable tool with a
  single decorator. The JSON schema is generated from the function's signature
  and docstring, so it never drifts out of sync.
- **A clean agent loop** — one `Agent` class, readable and ~60 lines.
- **Built-in example tools** — read a web page, count words, get the time.
- **A CLI** — `agent-harness "your task here"`.
- **A model-comparison script** — run one task across several models and compare
  how many steps each takes.
- **Tests with no network or API key** — the model client is mocked.

## Install

This project uses [uv](https://docs.astral.sh/uv/) (plain `pip` works too).

```bash
# clone your repo, then:
uv sync --extra dev        # or: pip install -e ".[dev]"
```

Add your OpenRouter key:

```bash
cp .env.example .env
# then edit .env and paste your key after OPENROUTER_API_KEY=
```

A free OpenRouter key works for everything here. Get one at
<https://openrouter.ai/settings/keys> and enable free models under
<https://openrouter.ai/settings/privacy>.

## Usage

From the command line:

```bash
agent-harness "Read https://example.com and tell me in one sentence what it is." -v
```

`-v` shows each step and tool call as it happens.

From Python:

```python
from agent_harness import Agent, ToolRegistry, build_client, load_settings

registry = ToolRegistry()

@registry.register(
    description="Add two numbers.",
    params={"a": "the first number", "b": "the second number"},
)
def add(a: float, b: float) -> str:
    return str(a + b)

settings = load_settings()
agent = Agent(build_client(settings), registry, model=settings.model)
print(agent.run("What is 2024 plus 1? Use your tool."))
```

See [`examples/`](examples/) for a runnable custom-tool demo and the
model-comparison script.

## How it works

```
         ┌──────────────────────────────────────────────┐
         │                  Agent.run()                   │
         │                                                │
 task ──▶ │  messages ──▶ model ──▶ tool_calls? ──┐        │
         │      ▲                     │  yes        │       │
         │      │                     ▼             │       │
         │      └──── tool results ◀─ ToolRegistry  │       │
         │                            .dispatch()   │       │
         │                     │ no                 │       │
         │                     ▼                     │       │
         │                final text answer ◀────────┘       │
         └──────────────────────────────────────────────┘
```

- [`config.py`](src/agent_harness/config.py) — load the key, build the client.
- [`tools.py`](src/agent_harness/tools.py) — the registry and schema generation.
- [`agent.py`](src/agent_harness/agent.py) — the loop.
- [`builtins.py`](src/agent_harness/builtins.py) — example tools.
- [`cli.py`](src/agent_harness/cli.py) — the command-line entry point.

## Tests

```bash
uv run pytest        # or: pytest
```

The tests use a scripted fake client, so they run offline and need no API key.

## Project layout

```
agent-harness/
├── src/agent_harness/   # the package
├── examples/            # runnable demos
├── tests/               # offline tests
├── docs/notes.md        # my learning notes
└── pyproject.toml
```


