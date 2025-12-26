# AGENTS.md - Pharmacist Assistant

## Project Overview

AI-powered pharmacist assistant for a retail pharmacy chain.

- **Python 3.13** with **uv** for package management
- **Chainlit** for conversational UI with streaming
- **OpenAI API** (vanilla - no LangChain)
- **SQLite** for database

## Commands

```bash
# Install dependencies
uv sync

# Run dev server (with hot reload)
uv run chainlit run main.py -w

# Run tests
uv run pytest                                      # all tests
uv run pytest tests/test_tools.py                  # single file
uv run pytest tests/test_tools.py::test_get_medication_info  # single test
uv run pytest -v                                   # verbose

# Lint & format
uv run ruff format .      # format
uv run ruff check .       # lint
```

## Code Style

### Imports

Standard library, then third-party, then local. Alphabetical within groups.

```python
import asyncio
import sqlite3
from typing import Any

import chainlit as cl
from openai import AsyncOpenAI

from db import get_connection
```

### Formatting

- Double quotes for strings
- 4-space indentation
- Trailing commas in multi-line structures

### Type Hints

Required for all function parameters and return types.

```python
async def get_medication_info(
    name: str | None = None,
    active_ingredient: str | None = None,
) -> dict[str, Any]:
```

### Naming

- `snake_case`: functions, variables, modules
- `PascalCase`: classes
- `UPPER_SNAKE_CASE`: constants
- `_prefix`: private functions/variables

### Async

- Use `async def` for all Chainlit handlers and OpenAI calls
- Use `AsyncOpenAI` client, not sync version

### Error Handling

Use specific exceptions, return structured error responses:

```python
try:
    result = await db_query(medication_name)
except sqlite3.Error as e:
    return {"error": f"Database error: {e}", "success": False}
```

### OpenAI Tools

Use Pydantic models to define tool parameters. This provides type safety, validation, and auto-generates OpenAI-compatible schemas via `model_json_schema()`.

### Database

- Parameterized queries only (no string concatenation)
- Use context managers for connections

## Key Constraints

1. **No LangChain** - vanilla OpenAI API only
2. **Stateless agent** - pass full conversation history each turn
3. **Bilingual** - support Hebrew and English
4. **No medical advice** - must not diagnose or recommend treatments
5. **Streaming required** - all responses stream in real-time
